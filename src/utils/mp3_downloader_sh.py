import asyncio
import subprocess


def generate_input_txt(video_tasks, input_path):
    with open(input_path, "w", encoding="utf-8") as f:
        for url, title, directory in video_tasks:
            f.write(f"{url}|{title}|{directory}\n")


def run_parallel_with_progress(input_txt_path: str, total_tasks: int):
    process = subprocess.Popen(
        [
            "stdbuf",
            "-oL",
            "bash",
            "./src/utils/download_mp3_parallel.sh",
            input_txt_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    downloaded = 0
    completed = 0

    for line in process.stdout:
        if "100%" in line:
            downloaded += 1
            percent = (downloaded / total_tasks) * 100
            print(f"downloaded {downloaded}/{total_tasks} ({percent:.1f}%)")

        if "Deleting original file" in line:
            completed += 1
            percent = (completed / total_tasks) * 100
            print(f"completed {completed}/{total_tasks} ({percent:.1f}%)")

    process.wait()
    if process.returncode == 0:
        print("✅ 다운로드 완료")
    else:
        print("❌ 오류 발생")
        print(process.stdout.read())


def download_mp3_parallel(video_tasks: list[tuple[str, str, str]]):
    generate_input_txt(video_tasks, "./tmp/" + video_tasks[0][2] + ".txt")
    run_parallel_with_progress(
        "./tmp/" + video_tasks[0][2] + ".txt", total_tasks=len(video_tasks)
    )


async def download_mp3_parallel_async(video_tasks: list[tuple[str, str, str]]):
    loop = asyncio.get_running_loop()
    generate_input_txt(video_tasks, "./tmp/" + video_tasks[0][2] + ".txt")

    await loop.run_in_executor(
        None,
        run_parallel_with_progress,
        "./tmp/" + video_tasks[0][2] + ".txt",
        len(video_tasks),
    )
