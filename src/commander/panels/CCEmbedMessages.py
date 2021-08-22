from typing import Dict

from discord.channel import TextChannel
from discord.message import Message
from discord_slash.model import ButtonStyle
from discord_slash.utils import manage_components

from src.commander.element.LyricsEmbed import LyricsEmbed
from src.commander.element.PlayerEmbed import PlayerEmbed
from src.commander.element.QueueEmbed import QueueEmbed
from src.commander.element.ReporterEmbed import ReporterEmbed
from src.commander.panels.Panel import Panel
from src.music.player import Player


class CCEmbedMessages(Panel):
    """Command Channel Panel with 4 messages and buttons"""

    def __init__(self, text_channel: TextChannel, **kwargs):
        """Generate initial Embeds based on the kwargs passed."""
        super().__init__(text_channel)
        self.players: Dict[int, Player] = kwargs["players"]
        self.expires = None
        self.id = "command_channel"

        # Front End Registration Objects
        self.reporter_message: Message = None
        self.lyrics_message: Message = None
        self.queue_message: Message = None
        self.player_message: Message = None

        self.cached_reporter_embed: ReporterEmbed = None
        self.cached_lyrics_embed: LyricsEmbed = None
        self.cached_queue_embed: QueueEmbed = None
        self.cached_player_embed: PlayerEmbed = None
        self.cached_components: Dict[str, ButtonStyle] = None

        # Initial Update
        # Embeds
        (
            self.reporter_embed,
            self.lyrics_embed,
            self.queue_embed,
            self.player_embed,
        ) = self.get_embeds()

        # Buttons
        self.components = self.get_buttons()

    @property
    def player(self) -> Player:
        if self.text_channel.guild.id in self.players:
            return self.players[self.text_channel.guild.id]

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

    def get_embeds(self):
        return (
            self.get_reporter_embed(),
            self.get_lyrics_embed(),
            self.get_queue_embed(),
            self.get_player_embed(),
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

    async def send_reporter_message(self):
        """Send/edit the reporter message."""
        if self.reporter_message:
            await self.reporter_message.edit(embed=self.reporter_embed)
        else:
            self.reporter_message = await self.text_channel.send(
                embed=self.reporter_embed
            )

    async def send_lyrics_message(self):
        """Send/edit the lyrics message."""
        if self.lyrics_message:
            await self.lyrics_message.edit(embed=self.lyrics_embed)
        else:
            self.lyrics_message = await self.text_channel.send(
                embed=self.lyrics_embed
            )

    async def send_queue_message(self):
        """Send/edit the queue message."""
        if self.queue_message:
            await self.queue_message.edit(embed=self.queue_embed)
        else:
            self.queue_message = await self.text_channel.send(
                embed=self.queue_embed
            )

    async def send_player_message(self):
        """Send/edit the player message."""
        if self.player_message:
            await self.player_message.edit(
                embed=self.player_embed, components=self.components
            )
        else:
            self.player_message = await self.text_channel.send(
                embed=self.player_embed, components=self.components
            )

    async def send(self):
        """Sends/edits the panel to the registered text_channel."""
        await self.send_reporter_message()
        await self.send_lyrics_message()
        await self.send_queue_message()
        await self.send_player_message()

    async def delete(self):
        """Deletes the panel from the registered text_channel."""
        await self.text_channel.delete_messages(
            [
                self.reporter_message,
                self.lyrics_message,
                self.queue_message,
                self.player_message,
            ]
        )
        self.reporter_message: Message = None
        self.lyrics_message: Message = None
        self.queue_message: Message = None
        self.player_message: Message = None

    async def process(self):
        """Custom process function to take advantage of caching."""
        self.reporter_embed = self.get_reporter_embed()
        if self.cached_reporter_embed != self.reporter_embed:
            await self.send_reporter_message()
            self.cached_reporter_embed = self.reporter_embed

        self.lyrics_embed = self.get_lyrics_embed()
        if self.cached_lyrics_embed != self.lyrics_embed:
            await self.send_lyrics_message()
            self.cached_lyrics_embed = self.lyrics_embed

        self.queue_embed = self.get_queue_embed()
        if self.cached_queue_embed != self.queue_embed:
            await self.send_queue_message()
            self.cached_queue_embed = self.queue_embed

        self.components = self.get_buttons()
        self.player_embed = self.get_player_embed()
        if (
            self.cached_components != self.components
            or self.cached_player_embed != self.player_embed
        ):
            await self.send_player_message()
            self.cached_player_embed = self.player_embed
            self.cached_components = self.components
