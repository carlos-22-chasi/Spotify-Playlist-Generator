class Track:
    '''
    Purpose:
        Track represents a piece of music on Spotify
    Instance Variables:
        name (str): name of the track
        id (int): the id of the spotify track
        artist (str): Artist of the track 
    Methods:
        __init__ -  initiallizes all of the intance variables
        create_spotify_uri - composes spotify uri to communicate with spotify web API
        __str__ - returns a string that contains the name and artist of a track 
    '''

    def __init__(self, name, id, artist):
        self.name = name
        self.id = id
        self.artist = artist

    def create_spotify_uri(self):
        return f"spotify:track:{self.id}"
    
    def __str__(self):
        return f"{self.name} by {self.artist}"