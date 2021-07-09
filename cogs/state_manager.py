from typing import Dict

from discord.ext import commands
from discord.ext.commands.bot import Bot

from config import FFMPEG_PATH
from src.element.database import DynamoDB
from src.music.player import Player
from src.preinitialization import clean_chat


class StateManager(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self._config_db: DynamoDB = None
        self.players: Dict[int, Player] = {}

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

    async def get_player(self, guild_id: int) -> Player:
        if guild_id not in self.players:
            self.players[guild_id] = Player(FFMPEG_PATH, self.bot)

            record = self.config_db.get_record(guild_id=guild_id)
            if record:
                if record.volume:
                    self.players[guild_id].volume = record.volume
                if record.command_channel_id:
                    command_channel = self.bot.get_channel(
                        record.command_channel_id
                    )
                    if command_channel:
                        # TODO: Replace when webhooks come
                        await clean_chat(command_channel)
                        await self.players[guild_id].register_command_channel(
                            command_channel
                        )

        return self.players[guild_id]


def setup(bot):
    bot.add_cog(StateManager(bot))
