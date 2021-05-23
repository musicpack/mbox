import logging
import discord
from src.music.player import Player
from src.commander.messenger import Messenger
from src.reporter import Reporter
from src.constants import VERSION, INVITE_LINK_FORMAT
from config import FFMPEG_PATH

class Profile:
    """Base class function representing one server. Creates a messenger, reporter, player object that manages the gui state of the command channel

    Args:
        guild (discord.Guild): The server this profile is tracking
        client (discord.Client): The client that is executing the operations
        command_channel (List[discord.TextChannel], discord.TextChannel, optional): The text channel that the profile should track for commands. Defaults to None.
            If None or a List of discord.TextChannels, setup() will request for a fix in discord 
    """
    def __init__(self, guild: discord.Guild, client: discord.Client, command_channel: discord.TextChannel = None) -> None:
        self.guild = guild
        self.valid_channels = command_channel
        self.messenger: Messenger = Messenger(guild.text_channels[0], client, self.valid_channels)
        self.player = Player(guild.voice_channels, ffmpeg_path=FFMPEG_PATH, messenger=self.messenger)
        self.reporter = Reporter(profile = self, messenger=self.messenger)

    async def setup(self):
        if type(self.valid_channels) == discord.TextChannel:
            # Update topic if out of date or malformed
            expected_topic = 'Music Box controlled channel. Chat in this channel will be deleted. Version ' + VERSION + ' ' + str(hash(self.valid_channels))
            if self.valid_channels.topic != expected_topic: await self.valid_channels.edit(topic = expected_topic) 

            # Setup all nessasary runtime objects here
            await self.messenger.setup()
            await self.player.setup()
            await self.reporter.setup()
        
        elif self.valid_channels == None:
            logging.debug('Guild [{}] is not set up. Sending request to set up.'.format(self.guild))

            err_msg = '⚠️Need to create new text channel.'
            act_msg = 'Created the new text channel \'music-box\''
            
            async def action_failed(text_channel):
                await text_channel.send('No reaction was sent. Leaving the server. Please add the bot again if you want to retry. ' + INVITE_LINK_FORMAT.format(self.messenger.client.user.id))
                await self.guild.leave()

            async def action_success(text_channel):
                music_box = await self.guild.create_text_channel(name='music-box')
                topic = 'Music Box controlled channel. Chat in this channel will be deleted. Version ' + VERSION + ' ' + str(hash(music_box))
                await music_box.edit(topic=topic)

                self.valid_channels = music_box
                self.messenger.command_channel = music_box
                await self.messenger.setup()
                await self.player.setup()
                await self.reporter.setup()
        
            await self.messenger.notify_action_required(err_msg, action_failed, action_success, act_msg)
        
        elif len(self.valid_channels) > 1:
            logging.debug('Guild [{}] has too many valid channels. Sending request to fix.'.format(self.guild))
            
            offending_channels = []
            for channel in self.valid_channels:
                offending_channels.append(channel.name)

            err_msg = '⚠️Need to remove topic of channels: ' + str(offending_channels)
            act_msg = 'Removed topic of all valid channels and created a new channel'
            
            async def action_failed(text_channel):
                await text_channel.send('No reaction was sent. Leaving the server. Please add the bot again if you want to retry. https://discord.com/api/oauth2/authorize?client_id=758005098042622194&permissions=8&scope=bot')
                await self.guild.leave()

            async def action_success(text_channel):
                for channel in self.valid_channels:
                    await channel.edit(topic='')
                
                music_box = await self.guild.create_text_channel(name='music-box')
                topic = 'Music Box controlled channel. Chat in this channel will be deleted. Version ' + VERSION + ' ' + str(hash(music_box))
                await music_box.edit(topic=topic)

                self.valid_channels = music_box
                self.messenger.command_channel = music_box
                await self.messenger.setup()
                await self.player.setup()
                await self.reporter.setup()

            await self.messenger.notify_action_required(err_msg, action_failed, action_success, act_msg)