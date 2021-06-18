
import logging
import discord
from base64 import b64encode
from discord.voice_client import VoiceClient
from src.element.MusicBoxContext import MusicBoxContext


async def play_ytid(id: str, context: MusicBoxContext):
    """Loads a youtube id to the player

    Args:
        id (str): youtube video id
        context (Context): context object (src.MusicBoxContext version)
    """
    base_url = 'https://www.youtube.com/watch?v='
    normalized_url = base_url+id
    voice_channel = context.determine_voice_channel()
    if(voice_channel): await context.profile.player.connect(voice_channel)
    await context.profile.player.play_youtube(normalized_url)

def get_player_client(context: MusicBoxContext) -> VoiceClient:
    if context.profile.player.connected_client:
        if context.profile.player.connected_client.is_connected():
            return context.profile.player.connected_client

async def player_prev(context: MusicBoxContext):
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

async def player_next(context: MusicBoxContext):
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

async def pause_player(context: MusicBoxContext) -> str:
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

async def resume_player(context: MusicBoxContext) -> str:
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

async def pubkey(context: MusicBoxContext) -> str:
    logging.info('Received pubkey from {0.name}'.format(context.message.author))

    # save public key in a base 64 encoded string
    pubkey_64 = b64encode(context.crypto.pubkey.save_pkcs1()).decode("utf-8")
    with open('mbox_public.key', 'r') as f:
        await context.message.reply(content= pubkey_64, file=discord.File(f))
        f.close()
    return

async def genkey(context: MusicBoxContext) -> None:
    if len(context.args) > 2:
        try:
            b64_encrypted_str = context.crypto.encrypt_token_x(context.args[1], context.args[2])
            await context.message.reply(content=b64_encrypted_str)
        except Exception as e:
            await context.message.reply(content=str(e))
        return

async def logout(context: MusicBoxContext) -> None:
    # TODO: add cleanup code and warnings to all profiles playing a song now.
    await context.bot.logout()
