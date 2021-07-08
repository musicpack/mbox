from typing import Dict

from discord.ext import commands

from config import FFMPEG_PATH
from src.element.database import DynamoDB
from src.music.player import Player


class StateManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._config_db: DynamoDB = None
        self.players: Dict[int:Player] = {}

    @property
    def config_db(self):
        if self._config_db is None:
            if self.bot.user is None or self.bot.user.id is None:
                # Raising the error here will lead to the cog not loading.
                # Workaround this problem by returning a Error instead.
                return ValueError(
                    "Bot variables not properly initialized. Wait until the bot is ready before creating a db."
                )

            self._config_db = DynamoDB(self.bot.user.id)

        return self._config_db

    def get_player(self, guild_id: int) -> Player:
        if guild_id not in self.players:
            # record = self.config_db.get_record(guild_id=guild_id)
            self.players[guild_id] = Player(FFMPEG_PATH, self.bot)

        return self.players[guild_id]


def setup(bot):
    bot.add_cog(StateManager(bot))
