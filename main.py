import os
from dotenv import load_dotenv

import urllib.parse
import requests
from flask import Flask, redirect, request, jsonify, session, url_for, render_template
from datetime import datetime

from spotifyclient import SpotifyClient

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

@app.route('/')
def index():
    return render_template('welcome_page.html')

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email user-read-recently-played playlist-modify-public'
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': redirect_uri,
        # 'show_dialog': True  # comment out later if not needed
    }
    auth_url = f'{AUTH_URL}?{urllib.parse.urlencode(params)}'
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({'error': request.args['error']})
    
    if 'code' in request.args:
        #get the access token and other important information
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        if response.status_code != 200 or 'access_token' not in token_info:
            return jsonify({'error': 'Failed to retrieve access token', 'response': token_info})
        
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
       
        #get the user id
        url = 'https://api.spotify.com/v1/me'
        headers = {
            'Authorization': f"Bearer {session['access_token']}"
        }
        user_response = requests.get(url, headers=headers)
        if user_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch user info', 'response': user_response.json()})
    
        user_info = user_response.json()
        session["user_id"] = user_info['id']

        return redirect('/login_success')
    
@app.route('/login_success')
def login_success():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh_token')
    
    return render_template('login_success.html') 

@app.route('/build_playlist')
def build_playlist():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh_token')
    
    spotify_client = SpotifyClient(session["access_token"], session['user_id'])

    # get last played tracks
    num_tracks_to_visualise = int(input("How many tracks would you like to visualise? "))
    last_played_tracks = spotify_client.get_last_played_tracks(num_tracks_to_visualise)

    print(f"\nHere are the last {num_tracks_to_visualise} tracks you listened to on Spotify:")
    for index, track in enumerate(last_played_tracks):
        print(f"{index+1}- {track}")

    # choose which tracks to use as a seed to generate a playlist
    indexes = input("\nEnter a list of up to 5 tracks you'd like to use as seeds. Use indexes separated by a space: ")
    indexes = indexes.split()
    seed_tracks = [last_played_tracks[int(index)-1] for index in indexes]

    # get recommended tracks based off seed tracks
    recommended_tracks = spotify_client.get_track_recommendations(seed_tracks)
    print("\nHere are the recommended tracks which will be included in your new playlist:")
    for index, track in enumerate(recommended_tracks):
        print(f"{index+1}- {track}")

    # get playlist name from user and create playlist
    playlist_name = input("\nWhat's the playlist name? ")
    playlist = spotify_client.create_playlist(playlist_name)
    print(f"\nPlaylist '{playlist.name}' was created successfully.")

    # populate playlist with recommended tracks
    spotify_client.populate_playlist(playlist, recommended_tracks)
    print(f"\nRecommended tracks successfully uploaded to playlist '{playlist.name}'.")

    # go to the playlist url to show the created playlist
    return redirect(url_for('confirm_playlist', playlist_id=playlist.id))

@app.route('/confirm_playlist/<playlist_id>')
def confirm_playlist(playlist_id):
    spotify_client = SpotifyClient(session["access_token"], session['user_id'])
    playlist = spotify_client.get_playlist(playlist_id)
    return render_template(
        'confirm_playlist_page.html', 
        playlist_name=playlist.name, 
        playlist_url=playlist.url, 
        playlist_id=playlist_id
    )

@app.route('/confirm_action', methods=['POST'])
def confirm_action():
    action = request.form['action']
    playlist_id = request.form['playlist_id']
    spotify_client = SpotifyClient(session["access_token"], session['user_id'])

    if action == 'delete':
        spotify_client.delete_playlist(playlist_id)
        return "Playlist deleted successfully."
    else:
        return "Playlist kept successfully."

@app.route('/refresh_token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    req_body = {
        'grant_type': 'refresh_token',
        'refresh_token': session['refresh_token'],
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    response = requests.post(TOKEN_URL, data=req_body)
    new_token_info = response.json()

    if response.status_code != 200 or 'access_token' not in new_token_info:
        return jsonify({'error': 'Failed to refresh access token', 'response': new_token_info})

    session['access_token'] = new_token_info['access_token']
    session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

    return redirect('/build_playlist')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
