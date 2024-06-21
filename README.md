# Spotify Playlist Generator
The Spotify Playlist Generator is a Python app that creates custom playlists based on users' Spotify listening history and preferences. It utilizes the Spotify Web API to recommend tracks and streamline playlist creation, enhancing the music discovery experience.

# Install
Install the necessary Python packages by running:
```bash 
$ pip install Flask
$ pip install python-dotenv
$ pip install requests
```

# Environment
Make sure to set up your environment variables in a .env file containing at least the following variables:
```bash 
SECRET_KEY=your_secret_key
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
REDIRECT_URI=your_redirect_uri
```
'SECRET_KEY': this can be any arbritary key used for cryptographic operations.

'CLIENT_ID': this is your Spotify application client ID. To obtain a client id, you need to create a Spotify Developer account and register a new application in the Spotify Developer Dashboard. Once registered, you'll recieve a client ID for the application.

'CLIENT_SECRET': this is the client secret associated with your Spotify application. Similar to the client ID, you'll get the client secret from the Spotify Developer Dashboard when you register your application.

REDIRECT_URI: This is the URI where Spotify will redirect the user after they authorize your application. My suggestion is 'http://localhost:5000/callback'

# Run
Run the main file and follow the console instructions:
```bash 
python main.py
```
