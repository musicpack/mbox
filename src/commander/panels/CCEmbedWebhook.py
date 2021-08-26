import logging
from time import time

from aiohttp import ClientSession
from discord.channel import TextChannel
from discord.embeds import Embed
from discord.errors import NotFound
from discord.ext import tasks
from discord.message import Message
from discord.webhook import AsyncWebhookAdapter, Webhook, WebhookMessage
from discord_slash.model import ButtonStyle
from discord_slash.utils import manage_components

from src.commander.element.LyricsEmbed import LyricsEmbed
from src.commander.element.PlayerEmbed import PlayerEmbed
from src.commander.element.QueueEmbed import QueueEmbed
from src.commander.element.ReporterEmbed import ReporterEmbed
from src.commander.panels.Panel import Panel
from src.constants import MUSIC_BOX_AVATAR_URL
from src.element.database import DynamoDB, Record
from src.music.player import Player


class CCEmbedWebhook(Panel):
    """Webhooks panel."""

    refresh_rate = 2  # seconds

    def __init__(self, text_channel: TextChannel, **kwargs):
        super().__init__(text_channel)
        self.players = kwargs.get("players", [])
        self.state = kwargs.get("state", None)
        self.config_db: DynamoDB = kwargs.get("config_db", None)

        self.webhook: Webhook = None
        self.webhook_message_id: int = None
        self._button_message: Message = None
        self._session = ClientSession()
        self.components = []

        self.cached_reporter_embed: ReporterEmbed = None
        self.cached_lyrics_embed: LyricsEmbed = None
        self.cached_queue_embed: QueueEmbed = None
        self.cached_player_embed: PlayerEmbed = None
        self.cached_components: list = []

        self.expires = None
        self.id = "command_channel"

    @property
    def player(self) -> Player:
        if self.text_channel.guild.id in self.players:
            return self.players[self.text_channel.guild.id]

    async def get_button_message(self) -> Message:
        if self._button_message is None:
            record: Record = self.config_db.get_record(
                self.text_channel.guild.id
            )
            if record and record.button_message_id:
                partial_message = self.text_channel.get_partial_message(
                    record.button_message_id
                )
                try:
                    full_message = await partial_message.fetch()
                    self._button_message = full_message
                    return full_message
                except NotFound:
                    pass

            sent_button_message = await self.text_channel.send(
                embed=Embed(title="Buttons"),
                components=self.components,
            )
            await sent_button_message.edit(
                suppress=True, components=self.components
            )
            record.button_message_id = sent_button_message.id
            self.config_db.store_record(record)
            self._button_message = sent_button_message
            return sent_button_message
        else:
            return self._button_message

    def get_reporter_embed(self) -> ReporterEmbed:
        """Getter for reporter_embed from factory."""
        return (
            ReporterEmbed(**vars(self.player))
            if self.player
            else ReporterEmbed()
        )

    def get_lyrics_embed(self) -> LyricsEmbed:
        """Getter for lyrics_embed from factory."""
        return (
            LyricsEmbed(**vars(self.player)) if self.player else LyricsEmbed()
        )

    def get_queue_embed(self) -> QueueEmbed:
        """Getter for queue_embed from factory."""
        return QueueEmbed(**vars(self.player)) if self.player else QueueEmbed()

    def get_player_embed(self) -> PlayerEmbed:
        """Getter for player_embed from factory."""
        return (
            PlayerEmbed(**vars(self.player)) if self.player else PlayerEmbed()
        )

    def get_buttons(self):
        # prev_button
        prev_button = manage_components.create_button(
            style=ButtonStyle.grey,
            custom_id="prev_button",
            emoji="⏮️",
        )

        # play_pause_button
        if self.player and self.player.paused is True:
            play_pause_button = manage_components.create_button(
                style=ButtonStyle.grey,
                custom_id="play_pause_button",
                emoji="▶️",
            )
        elif self.player and self.player.paused is False:
            play_pause_button = manage_components.create_button(
                style=ButtonStyle.grey,
                custom_id="play_pause_button",
                emoji="⏸️",
            )
        else:
            play_pause_button = manage_components.create_button(
                style=ButtonStyle.grey,
                custom_id="play_pause_button",
                emoji="⏯️",
            )

        # next_button
        next_button = manage_components.create_button(
            style=ButtonStyle.grey,
            custom_id="next_button",
            emoji="⏭️",
        )

        # volume_down_button
        volume_down_button = manage_components.create_button(
            style=ButtonStyle.grey,
            custom_id="volume_down_button",
            emoji="🔉",
        )

        # volume_up_button
        volume_up_button = manage_components.create_button(
            style=ButtonStyle.grey,
            custom_id="volume_up_button",
            emoji="🔊",
        )

        buttons = [
            prev_button,
            play_pause_button,
            next_button,
            volume_down_button,
            volume_up_button,
        ]

        action_row = manage_components.create_actionrow(*buttons)

        self.components = [action_row]
        return self.components

    def get_embeds(self):
        return (
            self.get_reporter_embed(),
            self.get_lyrics_embed(),
            self.get_queue_embed(),
            self.get_player_embed(),
        )

    async def update(self):
        # Embeds
        (
            self.reporter_embed,
            self.lyrics_embed,
            self.queue_embed,
            self.player_embed,
        ) = self.get_embeds()

        # Buttons
        self.components = self.get_buttons()

    async def send(self):
        """Send/edit the panel to the registered text_channel."""
        if not self.webhook:
            self.webhook = await self.get_webhook()

        if not self.webhook_message_id:
            record = self.config_db.get_record(self.text_channel.guild.id)
            if record and record.webhook_message_id:
                self.webhook_message_id = record.webhook_message_id
            else:
                await self.send_panel_set()
                return

        try:
            await self.edit_webhook_message(self.webhook_message_id)
        except NotFound:
            await self.send_panel_set()

    async def send_panel_set(self):
        """Send the webhook/buttons to the registered text_channel."""
        record = self.config_db.get_record(self.text_channel.guild.id)

        new_message_id = await self.send_webhook_message()
        self.webhook_message_id = new_message_id
        record.webhook_message_id = new_message_id
        self.config_db.store_record(record)

        await self.get_button_message()

    async def send_webhook_message(self) -> int:
        webhook_message: WebhookMessage = await self.webhook.send(
            wait=True,
            avatar_url=MUSIC_BOX_AVATAR_URL,
            embeds=[
                self.reporter_embed,
                self.lyrics_embed,
                self.queue_embed,
                self.player_embed,
            ],
        )
        return webhook_message.id

    async def edit_webhook_message(self, webhook_message_id: int):
        await self.webhook.edit_message(
            message_id=webhook_message_id,
            embeds=[
                self.reporter_embed,
                self.lyrics_embed,
                self.queue_embed,
                self.player_embed,
            ],
        )

    async def get_webhook(self) -> Webhook:
        record = self.config_db.get_record(self.text_channel.guild.id)

        if record and record.webhook_url:
            return Webhook.from_url(
                record.webhook_url,
                adapter=AsyncWebhookAdapter(self._session),
            )
        else:
            webhook = await self.text_channel.create_webhook(name="Music Box")
            record.webhook_url = webhook.url
            self.config_db.store_record(record)

            return webhook

    async def process(self):
        """Custom process function to take advantage of caching."""
        send = False
        self.reporter_embed = self.get_reporter_embed()
        if self.cached_reporter_embed != self.reporter_embed:
            send = True
            self.cached_reporter_embed = self.reporter_embed

        self.lyrics_embed = self.get_lyrics_embed()
        if self.cached_lyrics_embed != self.lyrics_embed:
            send = True
            self.cached_lyrics_embed = self.lyrics_embed

        self.queue_embed = self.get_queue_embed()
        if self.cached_queue_embed != self.queue_embed:
            send = True
            self.cached_queue_embed = self.queue_embed

        self.player_embed = self.get_player_embed()
        if self.cached_player_embed != self.player_embed:
            send = True
            self.cached_player_embed = self.player_embed

        if send:
            await self.send()

        self.components = self.get_buttons()
        if self.cached_components != self.components:
            button_message = await self.get_button_message()
            await button_message.edit(
                suppress=True, components=self.components
            )
            self.cached_components = self.components

    async def delete(self):
        raise NotImplementedError

    @tasks.loop(seconds=refresh_rate)
    async def task(self):
        if self.expires and self.expires < time():
            logging.info(
                f"Panel {self.text_channel.guild.id}:{self.id} expired."
            )
            self.delete_panel(self.text_channel.guild.id, panel_id=self.id)
            await self.process()
            await self._session.close()  # Close the active http session for webhook
            self.task.stop()
            return  # Exit the task loop

        if self.refresh_rate != self.task.seconds:
            self.task.change_interval(seconds=self.refresh_rate)
            self.task.restart()
            return

        await self.process()
