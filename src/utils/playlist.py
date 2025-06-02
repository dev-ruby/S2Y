import os

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException


load_dotenv()


sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
        client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
    )
)

from spotipy.exceptions import SpotifyException


def load_spotify_resource(url: str):
    try:
        if "open.spotify.com/playlist/" in url:
            resource_type = "playlist"
            resource_id = url.split("playlist/")[1].split("?")[0]
            resource = sp.playlist(resource_id)

            result = {
                "name": resource["name"],
                "id": resource["id"],
                "tracks": [
                    (track["track"]["name"], track["track"]["artists"][0]["name"])
                    for track in resource["tracks"]["items"]
                ],
            }

        elif "open.spotify.com/album/" in url:
            resource_type = "album"
            resource_id = url.split("album/")[1].split("?")[0]
            resource = sp.album(resource_id)

            result = {
                "name": resource["name"],
                "id": resource["id"],
                "tracks": [
                    (track["name"], track["artists"][0]["name"])
                    for track in resource["tracks"]["items"]
                ],
            }

        else:
            raise ValueError("Invalid Spotify URL: only album or playlist supported")

        return {"success": True, resource_type: result}

    except SpotifyException as e:
        if e.http_status == 404:
            return {
                "success": False,
                "error": f"The {resource_type} does not exist or is private",
            }
        else:
            return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}
