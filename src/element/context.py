from discord_slash.context import SlashContext
from src.element.profile import Profile
from typing import List
import discord
import logging

class Context:
    r"""Closely mimics (but does not fully inherit) a discord context :class:`~discord.ext.commands.context` to 
    include Music Box native elements and some SlashContext fields. 

    Represents the context in which a command is being invoked under.

    This class contains a lot of meta data to help you understand more about
    the invocation context.

    ## New fields

    prefix: :class:`str`
        The prefix that was used to invoke the command. Defaults to empty string.
        If context was a slash command, this should be '/'
    profile: :class:`.Profile`
        The profile matched to this context
    name: :class:`str`
        Name of the command
    slash_context: :class:`slash_context`
        ShashContext if context is a slash command. Defaults to none. Similar to prefix.
    

    ## Mimiced fields

    message: :class:`.Message`
        The message that triggered the command being executed.
    args: :class:`list`
        The list of transformed arguments that were passed into the command.
    kwargs: :class:`dict`
        A dictionary of transformed arguments that were passed into the command.
    
    ## Removed fields

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
        """Closely mimics (but does not fully inherit) a discord context :class:`~discord.ext.commands.context` to include Music Box native elements and some SlashContext fields.

        prefix: :class:`str`
            The prefix that was used to invoke the command. Defaults to empty string.
            If context was a slash command, this should be '/'
        profile: :class:`.Profile`
            The profile matched to this context
        name: :class:`str`
            Name of the command
        slash_context: :class:`slash_context`
            ShashContext if context is a slash command. Defaults to none. Similar to prefix.
        message: :class:`.Message`
            The message that triggered the command being executed.
        args: :class:`list`
            The list of transformed arguments that were passed into the command.
        kwargs: :class:`dict`
            A dictionary of transformed arguments that were passed into the command.
            
        """
        self.message: discord.Message = attrs.pop('message', None)
        self.args: List[str] = attrs.pop('args', [])
        self.kwargs: List[str] = attrs.pop('kwargs', {})
        self.prefix: str = attrs.pop('prefix', '')
        self.profile: Profile = attrs.pop('profile', None)
        self.name: str = attrs.pop('name', '')
        self.slash_context: SlashContext = attrs.pop('slash_context', None)
        
        self.verify_context()
    
    def get_str_full_input(self) -> str:
        if self.message:
            return self.message.content
        elif self.prefix == '/':
            return self.prefix + self.name + ' ' + ' '.join(self.args)
    
    def get_author(self) -> discord.Member:
        if self.message:
            return self.message.author
        elif self.slash_context:
            if self.slash_context.author:
                return self.slash_context.author

        return None

    def get_guild(self) -> discord.Guild:
        if self.profile:
            return self.profile.guild
        elif self.prefix == '/':
            if self.slash_context.guild:
                return self.slash_context.guild
        
        return None

    def verify_context(self) -> bool:
        """Checks to make sure fields are consistant and valid. Returns true if valid, throws error if not."""
        if self.message:
            if self.profile:
                if self.profile.messenger.command_channel != self.message.channel:
                    raise Exception('Profiles do not match up with the message. You are cross matching between two different servers.')
        if bool(self.slash_context) != (self.prefix == '/'):
            raise Exception('slash_context and prefix values do not line up')
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
        if self.profile.player:

            # CheckStateTrue: determine no voice channel if player already connected
            if(self.profile.player.connected_client):
                if self.profile.player.connected_client.is_connected():
                    return None
            
            # Save for later check, last connected channel
            last_connected_channel = self.profile.player.last_voice_channel

            # Save for later check, first voice channel
            if self.profile.guild.voice_channels:
                first_voice_channel = self.profile.guild.voice_channels[0]
        
        # Check slash_context exists
        if self.slash_context:

            # CheckStateTrue: join slash command user voice_channel if author in voice channel
            if self.slash_context.author:
                if self.profile:
                    for voice_channel in self.profile.guild.voice_channels:
                        if self.slash_context.author.id in voice_channel.voice_states.keys(): # this will get raw uncached voice states
                            return voice_channel

        # Check message exists
        if self.message:
            voice_channel : discord.VoiceChannel

            # CheckStateTrue: join message authors voice_channel if author in voice channel
            for voice_channel in self.message.guild.voice_channels:
                if self.message.author.id in voice_channel.voice_states.keys():
                    return voice_channel
        
        # CheckStateTrue: join last_connected_channel if exists
        if last_connected_channel:
            logging.warn(f'Determined last connected channel for guild {self.profile.guild.name}')
            return last_connected_channel
        
        # CheckStateTrue: join first available voice channel if exists
        if first_voice_channel:
            logging.warn(f'Determined first available voice channel for guild {self.profile.guild.name}')
            return first_voice_channel
        
        logging.error('Determined no possible voice channel to join.')
        return None