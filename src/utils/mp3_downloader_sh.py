import asyncio
import subprocess
from typing import Callable


def generate_input_txt(video_tasks, input_path):
    with open(input_path, "w", encoding="utf-8") as f:
        for url, title, directory in video_tasks:
            f.write(f"{url}|{title}|{directory}\n")



async def run_parallel_with_progress(input_txt_path: str, total_tasks: int, callback: Callable[[dict], None]):
    process = await asyncio.create_subprocess_exec(
        "stdbuf", "-oL", "bash", "./src/utils/download_mp3_parallel.sh", input_txt_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    downloaded = 0
    completed = 0

    assert process.stdout is not None  # for type checker
    async for raw_line in process.stdout:
        line = raw_line.decode().strip()

        if "100%" in line:
            downloaded += 1
            await callback({"type": "downloaded", "count": downloaded, "total": total_tasks})

        if "Completed" in line:
            completed += 1
            await callback({"type": "completed", "count": completed, "total": total_tasks})

    await process.wait()


async def download_mp3_parallel_async(video_tasks: list[tuple[str, str, str]], callback = Callable[[dict], None]):
    loop = asyncio.get_running_loop()
    generate_input_txt(video_tasks, "./tmp/" + video_tasks[0][2] + ".txt")
    
    await run_parallel_with_progress(
        "./tmp/" + video_tasks[0][2] + ".txt",
        len(video_tasks),
        callback,
    )

    # await loop.run_in_executor(
    #     None,
    #     run_parallel_with_progress,
    #     "./tmp/" + video_tasks[0][2] + ".txt",
    #     len(video_tasks),
    #     callback,
    # )
