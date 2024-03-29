from typing import Dict, Tuple

from ytmusicapi import YTMusic


def youtube_lyrics(youtube_id: str) -> Tuple[str, str, Dict]:
    """Gets lyrics (if exists) given the youtube id.
    NOTE: get_lyrics operation is wasteful as it discards a watch playlist while getting lyrics."""
    ytmusic = YTMusic()
    # TODO: Make more efficent use of watch_playlist
    watch_playlist = ytmusic.get_watch_playlist(videoId=youtube_id)

    browse_id = watch_playlist["lyrics"]
    if browse_id:
        result = ytmusic.get_lyrics(browse_id)
        return result["lyrics"], result["source"], watch_playlist

    return None, None, watch_playlist
