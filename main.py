import logging
import sys

import discord
from discord.ext import commands
from discord_slash import SlashCommand

from src.config import TOKEN

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

watching_channels = []

COMMAND_CHANNEL_WARNING = "Accepted command."

logging_level = logging.INFO
if len(sys.argv) > 1:
    if sys.argv[1] == "debug":
        logging_level = logging.DEBUG

logging.basicConfig(
    level=logging_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log", encoding="utf8"),
        logging.StreamHandler(),
    ],
)

initial_extensions = [
    "state_manager",
    "event_listener",
    "music_controller",
]

for filename in initial_extensions:
    bot.load_extension(f"cogs.{filename}")

bot.run(TOKEN)
