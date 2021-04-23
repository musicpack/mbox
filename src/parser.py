import logging
import re
from src.element.context import Context
import discord
from typing import List
from src.music.player import Player
from src.element.profile import Profile
from youtube_search import YoutubeSearch
from ytmusicapi import YTMusic

YTRE = '(?:youtube(?:-nocookie)?\\.com\\/(?:[^\\/\n\\s]+\\/\\S+\\/|(?:v|vi|e(?:mbed)?)\\/|\\S*?[?&]v=|\\S*?[?&]vi=)|youtu\\.be\\/)([a-zA-Z0-9_-]{11})'
YOUTUBE_ID_REGEX = re.compile(YTRE)

async def message(context: Context):
    logging.info('Parsing context [{0}]{1}: {2}'.format(context.get_guild(), context.get_author(), context.get_str_full_input()))

    # General bot command
    if context.name == '' or context.name == 'c' or context.name == 'play':
        user_input = ' '.join(context.args)

        match = YOUTUBE_ID_REGEX.findall(user_input)
        if match:
            youtube_id: str = match[0]
            await play_ytid(id = youtube_id, context = context)
        else:
            # search youtube for the phrase the user has typed

            # ytmusic = YTMusic()
            # results = ytmusic.search(query = message.content, limit = 1)
            # if results: await play_ytid(results[0]['videoId'], message, profile)
            results = YoutubeSearch(user_input, max_results=1).to_dict()
            if results:
                await play_ytid(id = results[0]['id'], context = context)

        return f"{user_input} accepted"
    
    return "Unknown commmand"

async def play_ytid(id: str, context: Context):
    """Loads a youtube id to the player

    Args:
        id (str): youtube video id
        profile (src.Profile): Profile of a server
        voice_channel (discord.VoiceChannel, optional): If provided, function will connect to this channel first. Defaults to None.
    """
    base_url = 'https://www.youtube.com/watch?v='
    normalized_url = base_url+id
    voice_channel = context.determine_voice_channel()
    if(voice_channel): await context.profile.player.connect(voice_channel)
    await context.profile.player.play_youtube(normalized_url)

async def pause_player(context: Context) -> str:
    if context.name == 'pause':
        if context.profile.player.connected_client:
            if context.profile.player.connected_client.is_connected():
                if not context.profile.player.connected_client.is_paused():
                    await context.profile.player.play_pause()  
                    return 'Paused player'
                else:
                    return 'Player is already paused'
        return 'Player not connected'
    else:
        logging.error('Context name is not pause. Cannot pause player')

async def resume_player(context: Context) -> str:
    if context.name == 'play':
        if context.profile.player.connected_client:
            if context.profile.player.connected_client.is_connected():
                if context.profile.player.connected_client.is_paused():
                    await context.profile.player.play_pause()  
                    return 'Resumed player'
                else:
                    return 'Player is already playing'
        return 'Player not connected'
    else:
        logging.error('Context name is not play. Cannot resume player')