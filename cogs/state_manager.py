from time import time
from typing import Dict, List

from discord.channel import TextChannel
from discord.ext import commands
from discord.ext.commands.bot import Bot

from config import FFMPEG_PATH
from src.commander.panels.CCEmbedMessages import CCEmbedMessages
from src.commander.panels.CCEmbedWebhook import CCEmbedWebhook
from src.commander.panels.Panel import Panel
from src.element.database import DynamoDB
from src.music.player import Player


class StateManager(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self._config_db: DynamoDB = None
        self.players: Dict[int, Player] = {}
        self.panels: Dict[str, Panel] = {}
        self.info_panels: Dict[int, List[Panel]] = {}

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

        return self.players[guild_id]

    def get_panel(
        self,
        text_channel: TextChannel,
        panel_id: str,
        panel_type: Panel,
    ) -> Panel:
        key = f"{text_channel.id}_{panel_id}"
        if key not in self.panels:
            self.panels[key] = panel_type(
                text_channel=text_channel,
                players=self.players,
                config_db=self._config_db,
            )

        return self.panels[key]

    async def process_command_channel_panel(self, guild_id: int):
        record = self.config_db.get_record(guild_id=guild_id)
        if record and record.command_channel_id:
            command_channel = self.bot.get_channel(record.command_channel_id)
            if command_channel:
                cc_panel = self.get_panel(
                    command_channel,
                    "command_channel",
                    CCEmbedWebhook,
                )
                cc_panel.refresh_time = time()

    async def process_info_panel(self, guild_id: int):
        if guild_id in self.info_panels:
            for panel in self.info_panels[guild_id]:
                panel.refresh_time = time()

    async def process_guild_panel(self, guild_id: int):
        await self.process_command_channel_panel(guild_id)
        await self.process_info_panel(guild_id)

    def add_info_panel(self, text_channel: TextChannel) -> Panel:

        # Create a list if doesnt exist
        if text_channel.guild.id not in self.info_panels:
            self.info_panels[text_channel.guild.id] = []

        panel_list = self.info_panels[text_channel.guild.id]

        panel_no = len(panel_list)
        panel_list.append(
            self.get_panel(text_channel, f"info_{panel_no}", CCEmbedMessages)
        )
        return panel_list[panel_no]


def setup(bot):
    bot.add_cog(StateManager(bot))
