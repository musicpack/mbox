import logging
import re
import discord
from typing import List
from src.music.player import Player
from src.profile import Profile
from youtube_search import YoutubeSearch

async def message(message: discord.Message, profile: Profile):
    
    logging.info('Parsing message from [{1.name}]{0.author}: {0.content}'.format(message, profile.guild))

    youtube = re.compile('(?:youtube(?:-nocookie)?\\.com\\/(?:[^\\/\n\\s]+\\/\\S+\\/|(?:v|vi|e(?:mbed)?)\\/|\\S*?[?&]v=|\\S*?[?&]vi=)|youtu\\.be\\/)([a-zA-Z0-9_-]{11})')
    
    match = youtube.findall(message.content)
    if match:
        youtube_id = match[0]
        await play_ytid(youtube_id, message, profile)
    else:
        results = YoutubeSearch(message.content, max_results=1).to_dict()
        if results:
            await play_ytid(results[0]['id'], message, profile)

async def play_ytid(id, message: discord.Message, profile: Profile):
    base_url = 'https://www.youtube.com/watch?v='
    normalized_url = base_url+id
    channel = determine_voice_channel(voice_channels= message.guild.voice_channels, message=message, profile=profile)

    if(channel):
        await profile.player.connect(channel)
    await profile.player.play_youtube(normalized_url)

def determine_voice_channel(voice_channels: List[discord.VoiceChannel], *, message: discord.Message = None, profile: Profile= None) -> discord.VoiceChannel:
    """Tries to determine the voice channel given context. Pass as much arguments possible for the best result.

    Args:
        voice_channels (List[discord.VoiceChannel])
        message (discord.Message): Message that caused this function to be called
        profile (Profile): Profile impacted
        player (Player): Used to check the connection state when message is also passed

    Returns:
        discord.VoiceChannel: Determined voice channel
        None: No suitable voice channel (player is already connected, no suitable voice_channels were given)
    """
    if profile.messenger.command_channel != message.channel:
        raise Exception('Profiles do not match up with the message. You are cross matching between two different servers.')

    last_connected_channel = None
    if profile.player:
        if(profile.player.connected_client):
            if profile.player.connected_client.is_connected():
                return None
        last_connected_channel = profile.player.last_voice_channel
                
    if message:
        voice_channel : discord.VoiceChannel
        for voice_channel in message.guild.voice_channels:
            if message.author.id in voice_channel.voice_states.keys():
                return voice_channel
    
    if last_connected_channel:
        return last_connected_channel
    else:
        if voice_channels:
            return voice_channels[0]
        elif profile:
            if profile.guild.voice_channels:
                return profile.guild.voice_channels[0]
        return None