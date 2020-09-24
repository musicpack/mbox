import discord
import os, sys
import logging

discord_token = os.environ.get('DiscordToken_mbox')
mbox = discord.Client()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

@mbox.event
async def on_ready():
    logging.info('Logged on as {0.user}'.format(mbox))

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
        logging.info('Received stop from {0.author}'.format(message.user))
        await mbox.logout()

mbox.run(discord_token)
