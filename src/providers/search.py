import asyncio
from concurrent.futures import ThreadPoolExecutor
from youtubesearchpython import VideosSearch

from src.utils.time import duration_to_seconds
from src.models.search_result import SearchResult

executor = ThreadPoolExecutor()


def get_middle_video_sync(query: str) -> SearchResult | None:
    """
    Search for videos in YouTube and return the middle one based on duration.

    Args:
        query (str): Search query for YouTube videos.

    Returns:
        SearchResult | None: An instance of SearchResult containing the query and the URL of the middle video.
                             If there are not enough videos, returns None.
    """

    search = VideosSearch(query, limit=4)
    videos = search.result()["result"]

    videos = [v for v in videos if v["duration"]]
    videos.sort(key=lambda v: duration_to_seconds(v["duration"]))

    if len(videos) >= 3:
        mid_video = videos[1]
        return SearchResult(query, mid_video["link"])
    else:
        return


async def get_middle_video_async(query: str) -> SearchResult | None:
    """
    Asynchronously search for videos in YouTube and return the middle one based on duration.

    Args:
        query (str): Search query for YouTube videos.

    Returns:
        SearchResult | None: An instance of SearchResult containing the query and the URL of the middle video.
                             If there are not enough videos, returns None.
    """

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, get_middle_video_sync, query)


async def search_all(queries: list[str]) -> list[SearchResult]:
    """
    Search for videos in YouTube for all queries and return the middle video for each.

    Args:
        queries (list[str]): List of search queries for YouTube videos.

    Returns:
        list[SearchResult]: A list of SearchResult instances containing the query and the URL of the middle video.
                            If there are not enough videos for a query, it will not be included in the results.
    """

    tasks = [get_middle_video_async(q) for q in queries]
    results = await asyncio.gather(*tasks)
    return [result for result in results if result is not None]
