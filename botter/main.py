from flask import Flask, render_template, url_for, request, redirect, Blueprint, session
import os, string, sys, urllib, base64, requests, six
from .run import run,add_track,play_track,pause_track,is_playing_track,get_now_playing
from . import db,socketio,join_room,leave_room
from datetime import datetime,date
from .models import User,Room
from flask_login import login_required, current_user

main = Blueprint('main',__name__)
scope = "user-modify-playback-state user-read-playback-state user-read-private"

client_id = str(os.environ['SPOTIFY_CLIENT_ID'])
client_secret = str(os.environ['SPOTIFY_CLIENT_SECRET'])

encoded_cred = base64.b64encode(six.text_type(client_id + ':' + client_secret).encode("ascii"))

# flask endpoints
@main.route("/dash")
@login_required
def dashboard():
    if current_user.access_token=="0":
        return render_template("dash.html", is_connected = False, name = current_user.name, client_id=client_id,scope=scope)
    return render_template("dash.html", is_connected = True, name = current_user.name, client_id=client_id,scope=scope)


@main.route("/")
def home():
    return render_template('home.html')


@main.route("/auth/")
def connect_spotify():
    authID = request.url
    authID = authID.split("?code=")[-1]
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "code": authID,
        "grant_type": "authorization_code",
        "redirect_uri": "https://listenbotter.herokuapp.com/auth/",
        "scope": scope
    }
    headers = {
        "Authorization": "Basic {}".format(encoded_cred.decode("ascii"))
    }
    response = requests.post(token_url, data=payload, headers=headers, verify=True, timeout=None)
    authID = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]
    token_duration = response.json()["expires_in"]


    current_user.access_token = authID
    current_user.refresh_token = refresh_token
    current_user.token_time = token_duration
    current_user.last_auth_time = datetime.now().strftime("%H:%M:%S")
    current_user.last_auth_date = str(date.today())

    db.session.commit()

    return redirect(url_for("main.dashboard"))


@main.route("/new_room/")
@login_required
def create_room():
    room_key = ''.join(random.choice(string.ascii_uppercase) for i in range(6))

    current_user.room_key = room_key
    db.session.commit()

    room = Room.query.filter_by(owner=current_user.email_id).first()
    if room:
        room.room_key = room_key
        room.connected_users = 1
    else:
        new_room = Room(room_key=room_key,owner=current_user.email_id,connected_users=1)
        db.session.add(new_room)

    db.session.commit()

    return render_template('new_room.html',key = room_key)


@main.route("/join_room/", methods=["GET", "POST"])
@login_required
def join_room_func():
    if request.method == "POST":
        room_key = request.form['room_key']
        if room_key=="":
            return render_template('join_room.html',error="Not a valid room key.")
        current_user.room_key = room_key
        db.session.commit()

        return redirect(url_for('main.room'))
    else:
        return render_template('join_room.html')


@main.route("/room/", methods=['POST','GET'])
@login_required
def room():
    room = Room.query.filter_by(room_key=current_user.room_key).first()
    if room and room.owner == current_user.email_id:
        return render_template('room.html',name = current_user.name, room = current_user.room_key, owner=True)
    else:
        return render_template('room.html', name=current_user.name, room=current_user.room_key, owner=False)


# socket-io routes

@socketio.on('message')
def message(data):
    if data['type']=='add_song':
        uri = data['uri']
        if not is_in_time():
            re_auth()
        add_track(current_user.access_token,uri)
        return
    socketio.send(data,room=data['room'])


@socketio.on('join_room')
def join(data):
    join_room(data['room'])
    socketio.send({'msg':data['name'] + ' has joined the room', 'type':"system"},room = data['room'])


@socketio.on('play')
def sockplay(data):
    if not is_in_time():
        re_auth()
    play_track(current_user.access_token)
    q = get_now_playing(current_user.access_token)
    if q:
        socketio.send({'track_info':q,'name':data['name'],'room':data['room'],'type':'track_info'},room=data['room'])


@socketio.on('pause')
def sockpause(data):
    if not is_in_time():
        re_auth()
    pause_track(current_user.access_token)


@socketio.on('leave_room')
def leave(data):
    leave_room(data['room'])
    socketio.send({'msg': current_user.name +' has left the room','type':'system'},room=data['room'])
    return redirect(url_for('main.dashboard'))

@socketio.on('add_song')
def add_song(data):
    socketio.emit("song_to_q", data, room=data['room'])
    #uri = data['uri']
    #if not is_in_time():
    #    re_auth()
    #if add_track(current_user.access_token,uri):
    #    socketio.send({'msg':data['track_name'] + " has been added to queue",'name':data['name'],'room':data['room'],'type':'system'},room=data['room'])



@socketio.on('search')
def search(data):
    if not is_in_time():
        re_auth()
    query = data['query']
    tracks = run(current_user.access_token,query)
    titles,imglinks,artists,uris = {},{},{},{}
    for i in range(5):
        if str(i) not in titles:
            titles['' + str(i)] = tracks[0][i]
        if str(i) not in imglinks:
            imglinks['' + str(i)] = tracks[1][i]
        if str(i) not in artists:
            artists['' + str(i)] = tracks[2][i]
        if str(i) not in uris:
            uris['' + str(i)] = tracks[3][i]

    socketio.send({'titles':titles,'artists':artists,'links':imglinks,'uris':uris,'name':data['name'],'room':data['room'],'type':data['type']},room=data['room'])


#misc functions
def re_auth():
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type":"refresh_token",
        "refresh_token":current_user.refresh_token
    }
    headers = {
        "Authorization": "Basic {}".format(encoded_cred.decode("ascii"))
    }
    response = requests.post(token_url, data=payload, headers=headers, verify=True, timeout=None)
    authID = response.json()["access_token"]
    token_duration = response.json()["expires_in"]

    current_user.access_token = authID
    current_user.token_time = token_duration
    current_user.last_auth_time = datetime.now().strftime("%H:%M:%S")
    current_user.last_auth_date = str(date.today())

    db.session.commit()


def is_in_time():
    if str(date.today())==current_user.last_auth_date:
        if current_user.last_auth_time[:2] == datetime.now().strftime("%H:%M:%S")[:2]:
            return True
    return False