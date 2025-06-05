import asyncio
import os
import re
from zipfile import ZipFile

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


async def delete_file_later(path: str, delay: int = 600):
    await asyncio.sleep(delay)
    if os.path.exists(path):
        os.remove(path)

def make_zip(zip_path: str, original_path: str, delete_original: bool = True):
    with ZipFile(zip_path, "w") as zipf:
        for root, _, files in os.walk(original_path):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    arcname=os.path.relpath(os.path.join(root, file), original_path),
                )
    if delete_original and os.path.exists(original_path):
        os.remove(original_path)
    