import os
import re
import shutil
import asyncio
from zipfile import ZipFile

from src.utils.playlist import load_spotify_resource
from src.utils.search import search_all
from src.utils.mp3_downloader_sh import download_mp3_parallel_async


def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


async def delete_file_later(path: str, delay: int = 600):
    await asyncio.sleep(delay)
    if os.path.exists(path):
        os.remove(path)


async def fetch_playlist(url, callback, pl_id):
    pl_data = load_spotify_resource(url)

    if pl_data["success"] is False:
        return {"success": False, "error_code": 400, "message": pl_data["error"]}

    pl_name = pl_data["playlist"]["name"]
    pl_name = sanitize_filename(pl_name)

    print("Search Start")

    pl = [
        {"name": track[0], "artist": track[1]}
        for track in pl_data["playlist"]["tracks"]
    ]

    # 병렬 검색 수행
    sr = await asyncio.gather(*(search_all([track]) for track in pl))

    dl = [(s[0]["link"], s[0]["original_query"]["name"], pl_id) for s in sr if s]

    await callback(
        {
            "type": "status",
            "status": "search_complete",
            "total_tracks": len(dl),
        }
    )

    await download_mp3_parallel_async(dl, callback)

    # 압축 최적화
    zip_path = f"./src/static/pl/{pl_id}.zip"
    with ZipFile(zip_path, "w") as zipf:
        tmp_dir = f"./tmp/{pl_id}"
        for root, _, files in os.walk(tmp_dir):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    arcname=os.path.relpath(os.path.join(root, file), tmp_dir),
                )

    shutil.rmtree(f"./tmp/{pl_id}")
    os.remove(f"./tmp/{pl_id}.txt")

    asyncio.create_task(delete_file_later(zip_path, delay=600))

    await callback(
        {
            "type": "success",
            "pl_name": pl_name,
            "download_url": f"/static/pl/{pl_id}.zip",
        }
    )
