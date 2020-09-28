import discord
import os, sys
import logging
import tasks.preinitialization
import asyncio

discord_token = os.environ.get('DiscordToken_mbox')
mbox = discord.Client()

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

@mbox.event
async def on_ready():
    logging.info('Logged on as {0.user}'.format(mbox))
    for server in mbox.guilds:
        logging.debug('Checking guild [{}] is set up'.format(server))
        valid_channel = tasks.preinitialization.valid_channels(server)
        if valid_channel: 
            watching_channels.append(valid_channel)
        else:
            logging.debug('Guild [{}] is not set up. Sending request to set up.'.format(server))
            await tasks.preinitialization.notify_not_setup(server, mbox)

@mbox.event
async def on_typing(channel, user, when):
    logging.debug('Typing from {0.name}'.format(user))

@mbox.event
async def on_guild_join(guild):
    logging.info('Joined Server: {0.name}'.format(guild))

@mbox.event
async def on_guild_remove(guild):
    logging.info('Removed from Server: {0.name}'.format(guild))

@mbox.event
async def on_message(message):
    if message.author == mbox.user:
        return

    logging.info('Message from {0.author}: {0.content}'.format(message))
    if message.content == 'stop':
        logging.info('Received stop from {0.name}'.format(message.author))
        await mbox.logout()

mbox.run(discord_token)
