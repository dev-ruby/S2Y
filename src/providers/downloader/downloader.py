import asyncio
import os

from typing import Callable
from src.models.search_result import SearchResult
from src.configs import Config


async def run_download_sh_async(
    input_txt_path: str, total_tasks: int, callback: Callable
):
    """
    Runs the download script asynchronously and reports progress via callback.

    Args:
        input_txt_path (str): Path to the input text file containing download tasks.
        total_tasks (int): Total number of tasks to be downloaded.
        callback (Callable): Callback function to report progress.
    """
    process = await asyncio.create_subprocess_exec(
        "stdbuf",
        "-oL",
        "bash",
        Config.path.DOWNLOADER_SCRIPT,
        input_txt_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    downloaded = 0
    completed = 0

    async for raw_line in process.stdout:
        line = raw_line.decode().strip()

        if "100%" in line:
            downloaded += 1
            await callback(
                {"type": "downloaded", "count": downloaded, "total": total_tasks}
            )

        if "Completed" in line:
            completed += 1
            await callback(
                {"type": "completed", "count": completed, "total": total_tasks}
            )

    await process.wait()


async def download_mp3_async(
    playlist_id: str, video_tasks: list[SearchResult], callback: Callable[[dict], None]
):
    """
    Downloads multiple MP3 files in parallel using a shell script.

    Args:
        video_tasks (list[SearchResult]): List of SearchResult objects containing video URLs and titles.
        callback (Callable[[dict], None]): Callback function to report progress.

    Returns:
        None
    """
    input_txt_path = Config.path.DOWNLOADER_INPUT_TXT.format(playlist_id)

    with open(input_txt_path, "w", encoding="utf-8") as f:
        for task in video_tasks:
            f.write(f"{task.url}|{task.query}|{playlist_id}\n")

    await run_download_sh_async(input_txt_path, len(video_tasks), callback)

    if os.path.exists(input_txt_path):
        os.remove(input_txt_path)
