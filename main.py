from src.element.context import Context
from typing import List, Union
import discord
import sys
import logging

import src.preinitialization
import src.parser
import src.element.profile
from src.constants import *
from discord_slash import SlashCommand
from discord_slash.context import SlashContext
from discord_slash.utils.manage_commands import create_option

mbox = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(mbox, sync_commands=True) 

COMMAND_CHANNEL_WARNING = 'Accepted command.'

logging_level = logging.INFO
if len(sys.argv) > 1:
    if sys.argv[1] == 'debug':
        logging_level = logging.DEBUG

logging.basicConfig(
    level=logging_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log", encoding='utf8'),
        logging.StreamHandler()
    ]
)

watching_channels = []
profiles: List[src.element.profile.Profile] = []
async def process_slash_command(ctx: SlashContext, f):
    for profile in profiles:
        if profile.guild == ctx.guild:
            mbox_ctx = Context(prefix='/',profile=profile,name=ctx.name,slash_context=ctx,message=ctx.message,args=ctx.args,kwargs=ctx.kwargs)
            if ctx.channel == profile.messenger.command_channel:
                await ctx.send(content=COMMAND_CHANNEL_WARNING)
                await f(mbox_ctx)
                await ctx.message.delete()
                return
            else:
                await ctx.defer(hidden=True)
                status = await f(mbox_ctx)
            break

    await ctx.send(content = f"{status}", hidden=True)

@slash.slash(name="c",
            description='General music-box command',
            options=[
               create_option(
                 name="command",
                 description="Input to message the bot as if sent to the command channel.",
                 option_type=3,
                 required=True
               )
             ])
async def _command(ctx: SlashContext, command: str):
    await process_slash_command(ctx, src.parser.message)

@slash.slash(name="pause",
            description='Pauses actively playing song')
async def _pause(ctx: SlashContext):
    await process_slash_command(ctx, src.parser.pause_player)

@slash.slash(name="next",
            description='Goes to the next song.')
async def _next(ctx: SlashContext):
    await process_slash_command(ctx, src.parser.player_next)
@slash.slash(name="skip",
            description='Goes to the next song.')
async def _skip(ctx: SlashContext):
    await process_slash_command(ctx, src.parser.player_next)

@slash.slash(name="prev",
            description='Goes to the previous song.')
async def _prev(ctx: SlashContext):
    await process_slash_command(ctx, src.parser.player_prev)
@slash.slash(name="back",
            description='Goes to the previous song.')
async def _back(ctx: SlashContext):
    await process_slash_command(ctx, src.parser.player_prev)

@slash.slash(name="Play",
            description='Plays or resumes a song.',
            options=[
               create_option(
                 name="song_name_or_link",
                 description="Adds this song to the queue.",
                 option_type=3,
                 required=False
               )
             ])
async def _play(ctx: SlashContext, song_name_or_link = None):
    if song_name_or_link:
        await process_slash_command(ctx, src.parser.message)
    else:
        await process_slash_command(ctx, src.parser.resume_player)
@slash.slash(name="Youtube",
            description='Add a youtube video to the queue.',
            options=[
               create_option(
                 name="search",
                 description="Name or link of a youtube video",
                 option_type=3,
                 required=True
               )
             ])
async def _youtube(ctx: SlashContext, search):
    await process_slash_command(ctx, src.parser.message)

@mbox.event
async def on_ready():
    logging.info('Logged on as {0.user}'.format(mbox))
    await src.preinitialization.generate_profiles(mbox.guilds, mbox, profiles)
    for profile in profiles:
        await profile.setup()

@mbox.event
async def on_typing(channel, user, when):
    logging.debug('Typing from {0.name}'.format(user))

@mbox.event
async def on_guild_join(guild: discord.Guild):
    logging.info(f'Joined Server: {guild.name}')
    try:
        await guild.text_channels[0].send('Thanks for adding Music Bot!')
        await src.preinitialization.generate_profile(guild, mbox, profiles)
        for profile in profiles:
            await profile.setup()
    except discord.errors.Forbidden:
        owner_member: discord.Member = guild.owner
        if owner_member:
            content = f"You or a member in server {guild.name} added me without the right permissions. Try adding me again with the link: " + INVITE_LINK_FORMAT.format(mbox.user.id)
            await owner_member.send(content=content)
        await guild.leave()

@mbox.event
async def on_guild_remove(guild):
    logging.info('Removed from Server: {0.name}'.format(guild))
    for profile in profiles:
        if profile.guild == guild:
            await profile.messenger.unregister_all()
            profiles.remove(profile)


@mbox.event
async def on_message(message: discord.Message):
    logging.debug('Message from {0.author}: {0.content}'.format(message))
    
    # Ignore message if it was from a bot
    if message.author.bot:
        # Delete the message if its from another bot.
        # Any message created by the bot itself should be handled outside of this function.
        if message.author != mbox.user:
            await message.delete()
        return

    # Top level command stop
    if message.content == 'stop':
        logging.info('Received stop from {0.name}'.format(message.author))
        await mbox.logout()
    
    # Check which profile the message relates to
    for profile in profiles:
        if profile.guild == message.guild:

            # Check if the message comes from a command channel
            if profile.messenger.command_channel == message.channel:
                await message.delete()

                # Create a context
                mbox_ctx = Context(prefix='',profile=profile,name='',slash_context=None,message=message,args=[message.content],kwargs={'command': message.content})

                # Top level command test
                if message.content == 'test':
                    logging.info('Received test from {0.name}'.format(message.author))
                    await profile.messenger.gui['player'].update()
                    break
                # Top level command rem
                if message.content == 'rem':
                    logging.info('Received rem from {0.name}'.format(message.author))
                    for action in profile.messenger.gui['player'].actions:
                        await action.remove_all()
                    break
                # Top level command play
                if message.content == 'play':
                    logging.info('Received play from {0.name}'.format(message.author))
                    await src.parser.play_ytid('JwmGruvGt_I', mbox_ctx)
                    break
                
                await src.parser.message(mbox_ctx)
                break

@mbox.event
async def on_reaction_add(reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
    if user != mbox.user:
        if reaction.message.author == mbox.user:
            await reaction.message.remove_reaction(reaction, user)

@mbox.event
async def on_voice_state_update(member, before, after):
    # Makes sure the player stops playing the song if the bot was disconnected by force
    if member == mbox.user:
        if before.channel and after.channel == None:
            for profile in profiles:
                if profile.guild == member.guild:
                    profile.player.stop()

mbox.run(TOKEN)
