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
        valid_server = await tasks.preinitialization.validate_server(server, mbox)
        if valid_server: 
            watching_channels.append(server)

@mbox.event
async def on_typing(channel, user, when):
    logging.debug('Typing from {0.name}'.format(user))

@mbox.event
async def on_guild_join(guild):
    logging.info('Joined Server: {0.name}'.format(guild))
    await guild.text_channels[0].send('Thanks for adding Music Bot!')
    valid_server = await tasks.preinitialization.validate_server(guild, mbox)
    if valid_server: 
        watching_channels.append(guild)

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
