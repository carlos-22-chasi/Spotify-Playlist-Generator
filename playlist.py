class Playlist:
    '''
    Purpose:
        Playlist represents a spotify playlist
    Instance Variables:
        name (str): name of the playlist
        id (int): the id of the spotify playlist

    Methods:
        __init__ -  initiallizes all of the intance variables
        __str__ - returns a string that contains the id of a playlist
    '''

    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.url = ''

    def __str__(self):
        return f"Playlist:{self.name}"
