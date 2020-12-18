import sys
from .spotify_client import SpotifyClient


def run(auth, query):
    spotify_client = SpotifyClient(auth)
    randomtracks = spotify_client.get_random_tracks(query)
    
    if randomtracks:
        return randomtracks
    else:
        return False

def add_track(auth,uri):
    spotify_client = SpotifyClient(auth)
    added = spotify_client.add_track_to_queue(uri)
    return added

def play_track(auth):
    spotify_client = SpotifyClient(auth)
    if not spotify_client.is_playing():
        spotify_client.play()

def pause_track(auth):
    spotify_client = SpotifyClient(auth)
    if not spotify_client.is_playing():
        spotify_client.pause()

def is_playing_track(auth):
    spotify_client = SpotifyClient(auth)
    return spotify_client.is_playing()

def get_now_playing(auth):
    spotify_client = SpotifyClient(auth)
    return spotify_client.now_playing()



