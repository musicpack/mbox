import tasks.player
import logging
import discord
from tasks.commander.messenger import Messenger

class Profile:
    def __init__(self, guild, client, command_channel = None) -> None:
        self.guild = guild
        self.valid_channels = command_channel
        self.ready = False
        self.messenger: Messenger = Messenger(guild.text_channels[0], client, self.valid_channels)
        self.player = tasks.player.Player(guild.voice_channels, ffmpeg_path='C:/Users/bliao/Desktop/mbox/ffmpeg-2020-09-30-git-9d8f9b2e40-full_build/bin/ffmpeg.exe', messenger=self.messenger)
    
    async def setup(self):
        if(not self.ready):
            if type(self.valid_channels) == discord.TextChannel:
                # Setup all nessasary runtime objects here
                await self.messenger.setup()
                self.ready = True
            
            elif self.valid_channels == None:
                logging.debug('Guild [{}] is not set up. Sending request to set up.'.format(self.guild))

                err_msg = '⚠️Need to create new text channel.'
                act_msg = 'Created the new text channel \'music-box\''
                
                async def action_failed(text_channel):
                    await text_channel.send('No reaction was sent. Leaving the server. Please add the bot again if you want to retry. https://discord.com/api/oauth2/authorize?client_id=758005098042622194&permissions=8&scope=bot')
                    await self.guild.leave()

                async def action_success(text_channel):
                    music_box = await self.guild.create_text_channel(name='music-box')
                    topic = 'Music Box controlled channel. Chat in this channel will be deleted. Version 0.1 ' + str(hash(music_box))
                    await music_box.edit(topic=topic)

                    self.valid_channels = music_box
                    self.messenger.command_channel = music_box
                    await self.messenger.setup()
                    self.ready = True
            
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
                    topic = 'Music Box controlled channel. Chat in this channel will be deleted. Version 0.1 ' + str(hash(music_box))
                    await music_box.edit(topic=topic)

                    self.valid_channels = music_box
                    self.messenger.command_channel = music_box
                    await self.messenger.setup()
                    self.ready = True

                await self.messenger.notify_action_required(err_msg, action_failed, action_success, act_msg)
        else:
            logging.info('Guild [{}] profile setup() call ignored (self.ready == true)')