import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from src.configs import Config
from src.models.music import Music
from src.models.playlist import Playlist

spotify_client = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=Config.spotify.CLIENT_ID,
        client_secret=Config.spotify.CLIENT_SECRET,
    )
)


def validate_spotify_url(url: str) -> bool:
    """
    Validate if the provided URL is a valid Spotify playlist or album URL.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is a valid Spotify playlist or album URL, False otherwise.
    """

    return url.startswith("https://open.spotify.com/") and (
        "playlist/" in url or "album/" in url
    )


def load_spotify_resource(url: str) -> Playlist:
    """
    Load a Spotify playlist or album from the provided URL.

    Args:
        url (str): The Spotify URL of the playlist or album.

    Raises:
        ValueError: If the URL is not a valid Spotify playlist or album URL.

    Returns:
        list[Music]: A list of Music objects containing track names and artists.
    """
    if not validate_spotify_url(url):
        raise ValueError("Invalid Spotify URL: only album or playlist supported")

    resource_type = "playlist" if "playlist/" in url else "album"
    resource_id = url.split(f"{resource_type}/")[1].split("?")[0]

    if resource_type == "playlist":
        resource = spotify_client.playlist(resource_id)
        musics = [
            Music(track["track"]["name"], track["track"]["artists"][0]["name"])
            for track in resource["tracks"]["items"]
        ]

    else:
        resource = spotify_client.album(resource_id)
        musics = [
            Music(track["name"], track["artists"][0]["name"])
            for track in resource["tracks"]["items"]
        ]

    return Playlist(resource["name"], musics)
