from flask import Flask, render_template, url_for, request, redirect, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required

auth = Blueprint('auth',__name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        remember = True if request.form['remember']=="True" else False
        user = User.query.filter_by(email_id=username).first()

        if not user or not check_password_hash(user.password,password):
            return render_template('login.html', error="Incorrect E-mail or password.")
        else:
            login_user(user,remember=remember)
            return redirect(url_for('main.dashboard'))
    else:
        return render_template('login.html')


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        if password == request.form['cpassword']:
            user = User.query.filter_by(email_id=username).first()
            if user:
                return render_template('signup.html', error="This user already exists.")
            else:
                new_user = User(email_id=username,password=generate_password_hash(password,method='sha256'),access_token="0",refresh_token="0",token_time=0,name=name,room_key="0",last_auth_date="0",last_auth_time="0")
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for("auth.login"))
        else:
            return render_template('signup.html', error = "The passwords do not match.")
    else:
        return render_template('signup.html')


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))