from fastapi import APIRouter
from src.models.playlist import PlaylistRequest
import os
from src.utils.playlist import load_spotify_resource
from src.utils.search import search_all
import shutil
from src.utils.mp3_downloader_sh import download_mp3_parallel_async
import asyncio
from zipfile import ZipFile
import time
import hashlib

router = APIRouter()


async def delete_file_later(path: str, delay: int = 600):
    await asyncio.sleep(delay)
    if os.path.exists(path):
        os.remove(path)


@router.post("/fetch-playlist")
async def fetch_playlist(request: PlaylistRequest):
    url = request.url

    pl_data = load_spotify_resource(url)

    if pl_data["success"] is False:
        return {"success": False, "error_code": 400, "message": pl_data["error"]}

    pl_name = pl_data["playlist"]["name"]
    pl_id = pl_data["playlist"]["id"] + str(time.time())
    pl_id = hashlib.sha256(pl_id.encode()).hexdigest()  # 해시값으로 변경하여 중복 방지

    print("Search Start")

    pl = [
        {"name": track[0], "artist": track[1]}
        for track in pl_data["playlist"]["tracks"]
    ]

    # 병렬 검색 수행
    sr = await asyncio.gather(*(search_all([track]) for track in pl))

    dl = [(s[0]["link"], s[0]["original_query"]["name"], pl_id) for s in sr if s]

    print("Search Complete")

    print("Download Start")
    # 병렬 다운로드 수행
    # await asyncio.gather(*(download_all_mp3([item]) for item in dl))
    await download_mp3_parallel_async(dl)
    print("Download Complete")

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

    return {
        "success": True,
        "download_url": f"/static/pl/{pl_id}.zip",
        "file_size": os.path.getsize(zip_path),
        "playlist_name": pl_name,
    }
