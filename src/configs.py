import os
from dotenv import load_dotenv

load_dotenv()

__all__ = ["Config"]


class PathConfig:
    STATIC_DIR = "./src/static/"
    TEMPLATES_DIR = "./src/templates/"
    TMP_DIR = "./tmp/"
    PLAYLIST_DIR = "./src/static/pl/"

    DOWNLOADER_SCRIPT = "./src/providers/downloader/download_mp3_parallel.sh"
    DOWNLOADER_INPUT_TXT = os.path.join(TMP_DIR, "{0}.txt")


class SpotifyConfig:
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


class Config:
    path = PathConfig()
    spotify = SpotifyConfig()
