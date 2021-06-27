import logging

from youtube_search import YoutubeSearch
from ytmusicapi import YTMusic


def youtube(phrase: str) -> str:
    """Searches Youtube using the phase and returns the top video result's ID

    Args:
        phrase (str): phrase to search youtube

    Returns:
        str: youtube video ID
    """
    results = YoutubeSearch(phrase, max_results=1).to_dict()
    if results:
        return results[0]["id"]
    logging.error("Youtube did not find any video.")


def youtube_music(phrase: str) -> str:
    """Searches Youtube Music using the phase and returns the top video result's ID

    Args:
        phrase (str): phrase to search Youtube Music

    Returns:
        str: youtube video ID
    """
    ytmusic = YTMusic()
    results = ytmusic.search(query=phrase)
    for result in results:
        if result["resultType"] == "video" or result["resultType"] == "song":
            return result["videoId"]
    # TODO: Notify user if youtube did not find any music in the command channel
    logging.error("Youtube Music did not find any music.")
