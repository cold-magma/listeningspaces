import random
import sys
import requests
import urllib


class SpotifyClient():
    def __init__(self, token):
        self.auth_token = token

    def get_random_tracks(self, query):
        url = 'https://api.spotify.com/v1/search?q={}&type=track&limit=5'.format(query)

        response = requests.get(url,
                                headers={
                                    "Content-Type": "application/json",
                                    "Authorization": "Bearer {}".format(self.auth_token)
                                })

        response_json = response.json()
        try:
            tracks_items = [track for track in response_json['tracks']['items']]
            titles = [track['name'] for track in tracks_items]
            uris = [track['uri'] for track in tracks_items]
            imglinks = [track['album']['images'][0]['url'] for track in tracks_items]
            artists = [track['artists'][0]['name'] for track in tracks_items]
            return [titles,imglinks,artists,uris]
        except KeyError:
            return False


    def add_track_to_queue(self,uri):
        url = "https://api.spotify.com/v1/me/player/queue?uri={}".format(uri)
        response = requests.post(url, headers={
                                    "Content-Type": "application/json",
                                    "Authorization": "Bearer {}".format(self.auth_token)
                                })

        return response.ok

    def is_playing(self):
        url = "https://api.spotify.com/v1/me/player"
        response = requests.get(url, headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.auth_token)
        })
        if str(response.status_code) == "204":
            return "no_track_queued"
        print(response)
        response_json = response.json()
        if response_json['is_playing']=="true":
            return "track_playing"
        return "no_track_playing"

            
    def skip_track(self,uri):
        skip_url = "https://api.spotify.com/v1/me/player/next"
        s_response = requests.post(url, headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.auth_token)
        })
        return True

    def play_track(self,uri):
        p_url = "https://api.spotify.com/v1/me/player/play"
        data = {"uris": [uri]}
        requests.put(p_url, headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.auth_token)
        })


    def play(self):
        p_url = "https://api.spotify.com/v1/me/player/play"
        requests.put(p_url, headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.auth_token)
        })

    
    def pause(self):
        p_url = "https://api.spotify.com/v1/me/player/pause"
        requests.put(p_url, headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.auth_token)
        })
        
    
    def now_playing(self):
        q = {}
        url = "https://api.spotify.com/v1/me/player"
        response = requests.get(url, headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.auth_token)
        })
        
        response_json = response.json()

        try:
            q['title'] = response_json['item']['name']
            q['artist'] = response_json['item']['artists'][0]['name']
            q['img'] = response_json['item']['album']['images'][0]['url']
            q['uri'] = response_json['item']['uri']
            q['pos'] = response_json['progress_ms']
            return q
        except KeyError:
            return False


    def sync(self,uri):
        url = "https://api.spotify.com/v1/me/player/play"

        payload = {
            'uris':["{}".format(uri)],
            'position_ms':0
        }

        response = requests.put(url,data=payload, headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.auth_token)
        })



        
        


