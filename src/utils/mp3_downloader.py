import yt_dlp
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re


executor = ThreadPoolExecutor()


def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


def download_mp3_sync(url: str, filename: str, d: str):
    print(url)
    filename = sanitize_filename(filename)
    os.makedirs("./tmp/" + d, exist_ok=True)
    full_path = os.path.join(f"./tmp/{d }", filename + ".%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": full_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }
        ],
        "noplaylist": True,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return os.path.join("./tmp/" + d, filename + ".mp3")


async def download_mp3_async(url: str, filename: str, d: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, download_mp3_sync, url, filename, d)


async def download_all_mp3(video_tasks: list[tuple[str, str, str]]):
    tasks = [download_mp3_async(url, filename, d) for url, filename, d in video_tasks]
    return await asyncio.gather(*tasks)
