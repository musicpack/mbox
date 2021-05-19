from src.element.context import Context
from typing import List, Union
import discord
import sys
import logging

import src.preinitialization
import src.parser
import src.element.profile
from src.constants import *
from discord_slash.utils.manage_commands import create_option
from discord.ext import commands
from discord_slash import SlashCommand
from config import TOKEN

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

watching_channels = []
profiles: List[src.element.profile.Profile] = []

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


@bot.event
async def on_message(message: discord.Message):
    logging.debug('Message from {0.author}: {0.content}'.format(message))

    # Ignore message if it was from a bot
    if message.author.bot:
        # Delete the message if its from another bot.
        # Any message created by the bot itself should be handled outside of this function.
        if message.author != bot.user:
            await message.delete()
        return

    # Top level command stop
    if message.content == 'stop':
        logging.info('Received stop from {0.name}'.format(message.author))
        await bot.logout()

    # Check which profile the message relates to
    for profile in profiles:
        if profile.guild == message.guild:

            # Check if the message comes from a command channel
            if profile.messenger.command_channel == message.channel:
                await message.delete()

                # Create a context
                bot_ctx = Context(prefix='', profile=profile, name='', slash_context=None, message=message, args=[
                    message.content], kwargs={'command': message.content})

                # Top level command test
                if message.content == 'test':
                    logging.info(
                        'Received test from {0.name}'.format(message.author))
                    await profile.messenger.gui['player'].update()
                    break
                # Top level command rem
                if message.content == 'rem':
                    logging.info(
                        'Received rem from {0.name}'.format(message.author))
                    for action in profile.messenger.gui['player'].actions:
                        await action.remove_all()
                    break
                # Top level command play
                if message.content == 'play':
                    logging.info(
                        'Received play from {0.name}'.format(message.author))
                    await src.parser.play_ytid('JwmGruvGt_I', bot_ctx)
                    break

                await src.parser.message(bot_ctx)
                break


@bot.event
async def on_typing(channel, user, when):
    logging.debug('Typing from {0.name}'.format(user))


@bot.event
async def on_guild_join(guild: discord.Guild):
    logging.info(f'Joined Server: {guild.name}')
    try:
        await guild.text_channels[0].send('Thanks for adding Music Bot!')
        await src.preinitialization.generate_profile(guild, bot, profiles)
        for profile in profiles:
            await profile.setup()
    except discord.errors.Forbidden:
        owner_member: discord.Member = guild.owner
        if owner_member:
            content = f"You or a member in server {guild.name} added me without the right permissions. Try adding me again with the link: " + \
                INVITE_LINK_FORMAT.format(bot.user.id)
            await owner_member.send(content=content)
        await guild.leave()


@bot.event
async def on_guild_remove(guild):
    logging.info('Removed from Server: {0.name}'.format(guild))
    for profile in profiles:
        if profile.guild == guild:
            await profile.messenger.unregister_all()
            profiles.remove(profile)


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
    if user != bot.user:
        if reaction.message.author == bot.user:
            await reaction.message.remove_reaction(reaction, user)


@bot.event
async def on_voice_state_update(member, before, after):
    # Makes sure the player stops playing the song if the bot was disconnected by force
    if member == bot.user:
        if before.channel and after.channel == None:
            for profile in profiles:
                if profile.guild == member.guild:
                    profile.player.stop()


@bot.event
async def on_ready():
    await src.preinitialization.generate_profiles(bot.guilds, bot, profiles)
    for profile in profiles:
        await profile.setup()

bot.load_extension("cogs.music_controller")

bot.run(TOKEN)
