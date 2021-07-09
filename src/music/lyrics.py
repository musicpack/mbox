from typing import Tuple
from ytmusicapi import YTMusic

def youtube_lyrics(youtube_id: str) -> Tuple[str, str, str, str]:
    """Gets lyrics (if exists) given the youtube id.
    NOTE: get_lyrics operation is wasteful as it discards a watch playlist while getting lyrics."""
    ytmusic = YTMusic()
    # TODO: Make more efficent use of watch_playlist
    watch_playlist = ytmusic.get_watch_playlist(videoId=youtube_id)

    browse_id = watch_playlist['lyrics']
    if browse_id:
        result = ytmusic.get_lyrics(browse_id)
        return result['lyrics'], result['source'], watch_playlist['tracks'][0]['title'], watch_playlist['tracks'][0]['artists'][0]['name']
        
    return None, None, watch_playlist['tracks'][0]['title'], watch_playlist['tracks'][0]['artists'][0]['name']
