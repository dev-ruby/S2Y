from src.models.music import Music

class Playlist:
    def __init__(self, name: str, tracks: list[Music]):
        self.name = name
        self.tracks = tracks
