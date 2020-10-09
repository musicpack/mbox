import discord
import os, sys
import logging
import tasks.preinitialization
import tasks.parser

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
profiles = []

@mbox.event
async def on_ready():
    logging.info('Logged on as {0.user}'.format(mbox))
    # for server in mbox.guilds:
    #     valid_server = await tasks.preinitialization.validate_server(server, mbox, watching_channels)
    await tasks.preinitialization.generate_profiles(mbox.guilds, mbox, profiles)
    for profile in profiles:
        if(not profile.ready):
            await profile.setup()
    print(len(profiles))

@mbox.event
async def on_typing(channel, user, when):
    logging.debug('Typing from {0.name}'.format(user))

@mbox.event
async def on_guild_join(guild):
    logging.info('Joined Server: {0.name}'.format(guild))
    await guild.text_channels[0].send('Thanks for adding Music Bot!')
    await tasks.preinitialization.generate_profile(guild, mbox, profiles)
    for profile in profiles:
        if(not profile.ready):
            await profile.setup()
    print(len(profiles))

@mbox.event
async def on_guild_remove(guild):
    logging.info('Removed from Server: {0.name}'.format(guild))
    for profile in profiles:
        if profile.guild == guild:
            profiles.remove(profile)
    print(len(profiles))


@mbox.event
async def on_message(message):
    if message.author == mbox.user:
        return

    logging.debug('Message from {0.author}: {0.content}'.format(message))
    if message.content == 'stop':
        logging.info('Received stop from {0.name}'.format(message.author))
        await mbox.logout()
    
    if message.channel in watching_channels:
        await message.delete()
        await tasks.parser.message(message)

mbox.run(discord_token)
