import logging
import re

from discord.voice_client import VoiceClient
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
    """Parses finding youtube id command context"""
    logging.info('Parsing context [{0}]{1}: {2}'.format(context.get_guild(), context.get_author(), context.get_str_full_input()))

    # General bot command
    if context.name == '' or context.name == 'c' or context.name == 'play' or context.name == 'youtube':
        user_input = ' '.join(context.args)

        match = YOUTUBE_ID_REGEX.findall(user_input)
        if match:
            youtube_id: str = match[0]
            await play_ytid(id = youtube_id, context = context)
        else:
            # search youtube for the phrase the user has typed
            if context.name == 'youtube':
                youtube_id = search_yt(user_input)
            else:
                youtube_id = search_ytmusic(user_input)
            if youtube_id: await play_ytid(youtube_id, context)

        return f"{user_input} accepted"
    
    return "Unknown commmand"

def search_yt(phrase: str) -> str:
    results = YoutubeSearch(phrase, max_results=1).to_dict()
    if results:
        return results[0]['id']
    logging.error('Youtube did not find any video.' + str(results))

def search_ytmusic(phrase: str) -> str:
    ytmusic = YTMusic()
    results = ytmusic.search(query = phrase)
    for result in results:
        if result['resultType'] == 'video' or result['resultType'] == 'song':
            return result['videoId']
    logging.error('Youtube Music did not find any music.' + str(results))

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

def get_player_client(context: Context) -> VoiceClient:
    if context.profile.player.connected_client:
        if context.profile.player.connected_client.is_connected():
            return context.profile.player.connected_client

async def player_prev(context: Context):
    if context.name == 'prev' or context.name == 'back':
        p_client = get_player_client(context)
        
        if p_client:
            result = context.profile.player.last()
            if result:
                return 'Playing previous song.'
            else:
                return 'No more songs to go back.'
        return 'Player not connected.'
    else:
        logging.error('Context name prev/back does not match function.')

async def player_next(context: Context):
    if context.name == 'skip' or context.name == 'next':
        p_client = get_player_client(context)
        
        if p_client:
            result = context.profile.player.next()
            if result:
                return 'Playing next song.'
            else:
                return 'Skipped. No more music to play.'
        return 'Player not connected.'
    else:
        logging.error('Context name next/skip does not match function.')

async def pause_player(context: Context) -> str:
    if context.name == 'pause':
        p_client = get_player_client(context)
        
        if p_client:
            if not p_client.is_paused():
                await context.profile.player.play_pause()  
                return 'Paused player'
            else:
                return 'Player is already paused'
        return 'Player not connected'
    else:
        logging.error('Context name is not pause. Cannot pause player')

async def resume_player(context: Context) -> str:
    if context.name == 'play':
        p_client = get_player_client(context)
        
        if p_client:
            if p_client.is_paused():
                await context.profile.player.play_pause()  
                return 'Resumed player'
            else:
                return 'Player is already playing'
        return 'Player not connected'
    else:
        logging.error('Context name is not play. Cannot resume player')