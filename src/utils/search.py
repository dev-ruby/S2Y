import asyncio
from concurrent.futures import ThreadPoolExecutor
from youtubesearchpython import VideosSearch

executor = ThreadPoolExecutor()


def duration_to_seconds(duration_str):
    parts = duration_str.split(":")
    parts = [int(p) for p in parts]
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = 0, parts[0], parts[1]
    else:
        h, m, s = 0, 0, parts[0]
    return h * 3600 + m * 60 + s


def get_middle_video_sync(query):
    search = VideosSearch(query["name"] + " - " + query["artist"], limit=3)
    videos = search.result()["result"]

    # duration 파싱 & 정렬
    videos = [v for v in videos if v["duration"]]  # 필터링: None 제거
    videos.sort(key=lambda v: duration_to_seconds(v["duration"]))

    if len(videos) >= 3:
        mid_video = videos[1]  # 중간값 (정렬된 리스트의 인덱스 1)
        return {
            "original_query": query,
            "title": mid_video["title"],
            "duration": mid_video["duration"],
            "link": mid_video["link"],
        }
    else:
        return


async def get_middle_video_async(query):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, get_middle_video_sync, query)


async def search_all(queries):
    tasks = [get_middle_video_async(q) for q in queries]
    return await asyncio.gather(*tasks)
