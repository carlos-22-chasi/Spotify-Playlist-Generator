import json
import requests
from track import Track
from playlist import Playlist

class SpotifyClient:
    '''
    Purpose:
        performs operation using the Spotify API
    Instance Variables:
        authorization_token (str): Spotify API token
        user_id (str): Spotify user id
    '''

    def __init__(self, authorization_token, user_id):
       self.authorization_token = authorization_token
       self.user_id = user_id

    '''
    Fetches the last played tracks of the user. 
    Args:
        limit (int): Number of tracks to fetch. Defaults to 10. Range is 0 - 50.
    Returns:
        list: A list of Track objects representing the last played tracks.
    '''
    def get_last_played_tracks(self, limit=10):
        url = f"https://api.spotify.com/v1/me/player/recently-played?limit={limit}"
        response = self._place_get_api_request(url)
        response_json = response.json()
        tracks = [Track(track["track"]["name"], track["track"]["id"], track["track"]["artists"][0]["name"]) for
                  track in response_json["items"]]
        return tracks
    
    '''
    Fetches track recommendations based on a list of seed tracks.
    Args:
        seed_tracks (list): List of Track objects to be used as seeds for recommendations.
        limit (int): Number of recommendations to fetch. Defaults to 50. Range is 0 - 100.
    Returns:
        list: A list of Track objects representing the recommended tracks.
    '''
    def get_track_recommendations(self, seed_tracks, limit=50):
        seed_tracks_url = ""
        for seed_track in seed_tracks:
            seed_tracks_url += seed_track.id + ","
        seed_tracks_url = seed_tracks_url[:-1]
        url = f"https://api.spotify.com/v1/recommendations?seed_tracks={seed_tracks_url}&limit={limit}"
        response = self._place_get_api_request(url)
        response_json = response.json()
        tracks = [Track(track["name"], track["id"], track["artists"][0]["name"]) for
                  track in response_json["tracks"]]
        return tracks
    
    '''
    Creates a new playlist with the specified name.
    Args:
        name (str): The name of the playlist to be created.
    Returns:
        Playlist: A Playlist object representing the created playlist.
    '''
    def create_playlist(self, name):
        data = json.dumps({
            "name": name,
            "description": "Recommended songs",
            "public": True
        })
        url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"
        response = self._place_post_api_request(url, data)
        response_json = response.json()

        # create playlist
        playlist_id = response_json["id"]
        playlist = Playlist(name, playlist_id)
        playlist.url = response_json['external_urls']['spotify']
        return playlist

    '''
    Adds tracks to the specified playlist.
    Args:
        playlist (Playlist): The Playlist object to which tracks will be added.
        tracks (list): List of Track objects to be added to the playlist.
    Returns:
        dict: The response JSON from the Spotify API.
    '''
    def populate_playlist(self, playlist, tracks):
        track_uris = [track.create_spotify_uri() for track in tracks]
        data = json.dumps(track_uris)
        url = f"https://api.spotify.com/v1/playlists/{playlist.id}/tracks"
        response = self._place_post_api_request(url, data)
        response_json = response.json()
        return response_json
    
    '''
    Fetches the details of a playlist by its ID.
    Args:
        playlist_id (str): The ID of the playlist to be fetched.
    Returns:
        Playlist: A Playlist object representing the fetched playlist.
    '''
    def get_playlist(self, playlist_id):
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        response = self._place_get_api_request(url)
        response_json = response.json()
        playlist = Playlist(response_json['name'], playlist_id)
        playlist.url = response_json['external_urls']['spotify']
        return playlist

    '''
    Deletes the specified playlist.
    Args:
        playlist_id (str): The ID of the playlist to be deleted.
    Returns:
        bool: True if the playlist was successfully deleted, False otherwise.
    '''
    def delete_playlist(self, playlist_id):
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/followers"
        response = requests.delete(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.authorization_token}"
            }
        )
        return response.status_code == 200
     
    '''
    Makes a GET request to the specified URL with the appropriate headers.
    Args:
        url (str): The URL to make the GET request to.
    Returns:
        requests.Response: The response from the GET request.
    '''
    def _place_get_api_request(self, url):
        response = requests.get(
            url, 
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.authorization_token}"
            }
        )
        return response
    
    '''
    Makes a POST request to the specified URL with the appropriate headers and data.
    Args:
        url (str): The URL to make the POST request to.
        data (str): The data to be sent in the POST request.
    Returns:
        requests.Response: The response from the POST request.
    '''
    def _place_post_api_request(self, url, data):
        response = requests.post(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.authorization_token}"
            }
        )
        return response