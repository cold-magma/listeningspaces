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
    if spotify_client.is_playing() == "no_track_queued":
        spotify_client.play_track(uri)
        return True
    else
        added = spotify_client.add_track_to_queue(uri)
        spotify_client.skip_track()
        return added

def play_track(auth):
    spotify_client = SpotifyClient(auth)
    if spotify_client.is_playing() == "no_track_playing":
        spotify_client.play()

def pause_track(auth):
    spotify_client = SpotifyClient(auth)
    if spotify_client.is_playing() == "track_playing":
        spotify_client.pause()

def is_playing_track(auth):
    spotify_client = SpotifyClient(auth)
    return spotify_client.is_playing()

def get_now_playing(auth):
    spotify_client = SpotifyClient(auth)
    return spotify_client.now_playing()



