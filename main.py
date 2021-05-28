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

bot.load_extension("cogs.music_controller_listeners")
bot.load_extension("cogs.music_controller")


bot.run(TOKEN)

"""
from typing import List
import discord
import sys
import logging

import src.preinitialization
import src.parser
import src.element.profile
from discord_slash.utils.manage_commands import create_option
from discord.ext import commands
from discord_slash import SlashCommand
from config import TOKEN
from src.constants import *

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


bot.load_extension("cogs.music_controller")
bot.load_extension("cogs.music_controller_listeners")

bot.run(TOKEN)
"""