import os
import uuid
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.schemas.playlist import PlaylistRequest
from src.services.fetch_playlist_service import fetch_playlist as fetch_playlist_service


router = APIRouter()

progress_connections = {}


@router.websocket("/ws/progress/{task_id}")
async def progress_ws(websocket: WebSocket, task_id: str):
    await websocket.accept()
    progress_connections[task_id] = websocket

    try:
        while True:
            await websocket.send_json({"type": "ping"})
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        progress_connections.pop(task_id, None)


async def delete_file_later(path: str, delay: int = 600):
    await asyncio.sleep(delay)
    if os.path.exists(path):
        os.remove(path)


async def progress_callback(task_id: str, data: dict):
    ws = progress_connections.get(task_id)

    if ws:
        await ws.send_json(data)


@router.post("/fetch-playlist")
async def fetch_playlist(request: PlaylistRequest):
    url = request.url
    task_id = str(uuid.uuid4())
    callback = lambda data: progress_callback(task_id, data)
    asyncio.create_task(fetch_playlist_service(url, callback, task_id))

    return {"task_id": task_id}
