import os
import re
import shutil
import asyncio
from zipfile import ZipFile
from typing import Callable

from src.providers.spotify import load_spotify_resource
from src.providers.search import search_all
from src.providers.downloader import download_mp3_async
from src.utils.file import sanitize_filename, delete_file_later, make_zip




async def fetch_playlist(url: str, callback: Callable, playlist_id: str):
    """
    Fetches a Spotify playlist, searches for each track, downloads them,
    and compresses the results into a zip file.

    Args:
        url (str): The Spotify playlist URL.
        callback (Callable): A callback function to report progress.
        playlist_id (str): Unique identifier for the playlist.

    Returns:
        None
    """
    
    await callback({
        "type": "status",
        "message": "Fetching playlist data...",
    })
    
    playlist = load_spotify_resource(url)
    playlist_name = sanitize_filename(playlist.name)
    
    querys = [f"{track.title} - {track.artist}" for track in playlist.tracks]
    
    search_results = await search_all(querys)
    
    await callback({
        "type": "status",
        "message": f"Downloading <code>{playlist.tracks[0].title}</code> and {len(playlist.tracks)-1} more tracks...",
    })

    await download_mp3_async(
        playlist_id,
        search_results,
        callback
    )
    
    make_zip(f"./src/static/pl/{playlist_id}.zip", f"./tmp/{playlist_id}")

    asyncio.create_task(delete_file_later(f"./src/static/pl/{playlist_id}.zip", delay=600))

    await callback(
        {
            "type": "success",
            "pl_name": playlist_name,
            "download_url": f"/static/pl/{playlist_id}.zip",
        }
    )
    