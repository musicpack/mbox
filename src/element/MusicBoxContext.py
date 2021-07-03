import logging
from typing import Text

import discord
from discord.channel import TextChannel, VoiceChannel
from discord.ext.commands.context import Context
from discord.guild import Guild
from discord_slash.context import SlashContext

from src.auth import Crypto
from config import FFMPEG_PATH
from discord.client import Client
from src.music.player import Player


class MusicBoxContext(Context):
    r"""Inherits a discord context :class:`~discord.ext.commands.context` to
    include Music Box native elements and some SlashContext fields.

    Represents the context in which a command is being invoked under.

    This class contains a lot of meta data to help you understand more about
    the invocation context.

    ## New fields

    profile: :class:`.Profile`
        The profile matched to this context
    slash_context: :class:`slash_context`
        ShashContext if context is a slash command. Defaults to none. Similar to prefix.

    # Imported fields

    message: :class:`.Message`
        The message that triggered the command being executed.
    args: :class:`list`
        The list of transformed arguments that were passed into the command.
        If this is accessed during the :func:`on_command_error` event
        then this list could be incomplete.
    kwargs: :class:`dict`
        A dictionary of transformed arguments that were passed into the command.
        Similar to :attr:`args`\, if this is accessed in the
        :func:`on_command_error` event then this dict could be incomplete.
    prefix: :class:`str`
        The prefix that was used to invoke the command.
    command: :class:`Command`
        The command that is being invoked currently.
    invoked_with: :class:`str`
        The command name that triggered this invocation. Useful for finding out
        which alias called the command.
    invoked_subcommand: :class:`Command`
        The subcommand that was invoked.
        If no valid subcommand was invoked then this is equal to ``None``.
    subcommand_passed: Optional[:class:`str`]
        The string that was attempted to call a subcommand. This does not have
        to point to a valid registered subcommand and could just point to a
        nonsense string. If nothing was passed to attempt a call to a
        subcommand then this is set to ``None``.
    command_failed: :class:`bool`
        A boolean that indicates if the command failed to be parsed, checked,
        or invoked.
    bot: :class:`.Bot`
        The bot that contains the command being executed.
    """

    def __init__(self, **attrs):
        """Inherits a discord context :class:`~discord.ext.commands.context` to
        include Music Box native elements and some SlashContext fields.

        ## New fields

        guild: :class:`.Guild`
            The guild matched to this context
        command_channel: :class:`.TextChannel`
            The command_channel matched to this context
        player: :class:`.Player`
            The player matched to this context
        slash_context: :class:`slash_context`
            ShashContext if context is a slash command. Defaults to none. Similar to prefix.

        ## Essential attributes used in the MusicBox program

        prefix: :class:`str`
            The prefix that was used to invoke the command. Defaults to empty string.
            If context was a slash command, this should be '/'
        message: :class:`.Message`
            The message that triggered the command being executed.
        args: :class:`list`
            The list of transformed arguments that were passed into the command.
        kwargs: :class:`dict`
            A dictionary of transformed arguments that were passed into the command.

        """
        self.guild: Guild = attrs.pop("guild")
        self.command_channel: TextChannel = attrs.pop("command_channel")
        self.player: Player = attrs.pop("Player")(ffmpeg_path=FFMPEG_PATH, client= attrs.pop("client"))
        self.name: str = attrs.pop("name", "")
        self.slash_context: SlashContext = attrs.pop("slash_context", None)
        self.crypto: Crypto = attrs.pop("crypto", None)

        # workaround: make _state object since super() expects one (regardless of message=null)
        class FakeMessage(NotImplementedError):
            pass

        if attrs["message"] is None:
            a = FakeMessage()
            a._state = NotImplementedError
            attrs["message"] = a

        super().__init__(**attrs)

        # fix self.message to not be a fake message
        if isinstance(self.message, FakeMessage):
            self.message = None
        self.verify_context()

    def get_str_full_input(self) -> str:
        if self.message:
            return self.message.content
        elif self.prefix == "/":
            return self.prefix + self.name + " " + " ".join(self.args)

    def get_author(self) -> discord.Member:
        if self.message:
            return self.message.author
        elif self.slash_context:
            if self.slash_context.author:
                return self.slash_context.author

        return None

    def get_guild(self) -> discord.Guild:
        if self.guild:
            return self.guild
        elif self.prefix == "/":
            if self.slash_context.guild:
                return self.slash_context.guild

        return None

    def verify_context(self) -> bool:
        """Checks to make sure fields are consistant and valid. Returns true if valid, throws error if not."""
        if bool(self.slash_context) != (self.prefix == "/"):
            raise Exception("slash_context and prefix values do not line up")
        return True

    def determine_voice_channel(self) -> discord.VoiceChannel:
        """Tries to determine the voice channel to connect the player given context.

        Returns:
            discord.VoiceChannel: Determined voice channel
            None: No suitable voice channel (player is already connected, no suitable voice_channels were given)
        """
        last_connected_channel = None
        first_voice_channel = None

        # Priority is based from the code top to bottom. if state is true (CheckStateTrue sections) then code will end determination

        # Check player exists
        if self.player:
            first_voice_channel = self.return_voice_channel_for_player()
            if(not first_voice_channel):
                return None
        
        # Check slash_context exists
        if self.slash_context:
            voice_channel_slash_context = self.return_voice_channel_for_slash_context()
            if(voice_channel_slash_context):
                return voice_channel_slash_context
        
        # Check message exists
        if self.message:
            voice_channel: discord.VoiceChannel
            voice_channel = self.return_voice_channel_for_message(voice_channel)
            if(voice_channel):
                return voice_channel

        # CheckStateTrue: join last_connected_channel if exists
        if last_connected_channel:
            logging.warn(
                f"Determined last connected channel for guild {self.guild.name}"
            )
            return last_connected_channel

        # CheckStateTrue: join first available voice channel if exists
        if first_voice_channel:
            logging.warn(
                f"Determined first available voice channel for guild {self.guild.name}"
            )
            return first_voice_channel

        logging.error("Determined no possible voice channel to join.")
        return None

    def return_voice_channel_for_player(self) -> VoiceChannel:
        """Looks at the player object and decides if a voice channel exists 

        Returns:
            VoiceChannel: The voice_channel associated with the player
        """
        # CheckStateTrue: determine no voice channel if player already connected
        if self.player.connected_client:
            if self.player.connected_client.is_connected():
                return None

        # Save for later check, first voice channel
        if self.guild.voice_channels:
            return self.guild.voice_channels[0]
    
    def return_voice_channel_for_slash_context(self) -> VoiceChannel:
        """Looks at the slash_context object and decides if a voice channel exists

        Returns:
            VoiceChannel: The voice_channel associated with the slash_context
        """
        # CheckStateTrue: join slash command user voice_channel if author in voice channel
        if self.slash_context.author:
            if self.guild:
                for voice_channel in self.guild.voice_channels:
                    if (
                        self.slash_context.author.id
                        in voice_channel.voice_states.keys()
                    ):  # this will get raw uncached voice states
                        return voice_channel
    
    def return_voice_channel_for_message(self, voice_channel: VoiceChannel) -> VoiceChannel:
        """Looks at the message object and decides if a voice channel exists

        Args:
            voice_channel (VoiceChannel): The voice_channel associated with the message

        Returns:
            VoiceChannel: The voice_channel associated with the message
        """
        # CheckStateTrue: join message authors voice_channel if author in voice channel
        for voice_channel in self.message.guild.voice_channels:
            if self.message.author.id in voice_channel.voice_states.keys():
                return voice_channel

