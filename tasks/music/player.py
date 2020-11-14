from discord.player import AudioSource
import youtube_dlc
import discord
import logging
import asyncio
import os
from tasks.commander.messenger import Messenger
from tasks.commander.element.Button import Button
from tasks.commander.element.ChatEmbed import ChatEmbed
from tasks.music.element.MusicSource import MusicSource
from tasks.music.element.cache import Cache

YOUTUBE_ICON = 'https://yt3.ggpht.com/a/AATXAJxHHP_h8bUovc1qC4c07sVXxVbp3gwDEg-iq8gbFQ=s100-c-k-c0xffffffff-no-rj-mo'
DOWNLOAD_PATH = os.path.join('cache', 'youtube')

class Player:
    def __init__(self, voice_channels, ffmpeg_path, messenger: Messenger) -> None:
        self.connected_client: discord.VoiceClient = None
        self.voice_channels = voice_channels
        self.messenger: Messenger = messenger
        self.playlist = []
        self.buttons = {
            'play_pause': Button(emoji='⏯️', client = self.messenger.client, action=self.play_pause),
            'toggle_description': Button(emoji='💬', client = self.messenger.client, action=self.toggle_description),
            'lower_volume': Button(emoji='🔉', client = self.messenger.client, action=self.lower_volume),
            'raise_volume': Button(emoji='🔊', client = self.messenger.client, action=self.raise_volume)
        }
        self.ChatEmbed : ChatEmbed = None
        self.cache = Cache()

        self.ffmpeg_path = ffmpeg_path
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
            # ,'options': '-vn -ss 40'
        }
        self.ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s')
        }
        self.description = None
        self.display = False
        self.read = 0
    
    async def setup(self):
        self.ChatEmbed = self.messenger.gui['player']
        self.ChatEmbed.actions = [self.buttons['play_pause'],self.buttons['toggle_description'],self.buttons['lower_volume'],self.buttons['raise_volume']]
        self.ChatEmbed.embed.title = 'Not Playing'
        await self.ChatEmbed.update()

    async def lower_volume(self):
        self.connected_client.source.volume -= .1
        print(self.connected_client.source.volume)

    async def raise_volume(self):
        self.connected_client.source.volume += .1
        print(self.connected_client.source.volume)


    def stop(self):
        return self.connected_client.stop()
    
    def pause(self):
        return self.connected_client.pause()

    def resume(self):
        return self.connected_client.resume()
    
    async def toggle_description(self):
        if self.description:
            if self.display:
                self.ChatEmbed.embed.description = self.description[0:150] + '...'
                self.display = False
                await self.ChatEmbed.update()
            else:
                self.ChatEmbed.embed.description = self.description[0:2048]
                self.display = True
                await self.ChatEmbed.update()
        
    
    async def play_pause(self):
        if self.connected_client:
            if self.connected_client.is_playing():
                self.pause()
            elif self.connected_client.is_paused():
                self.resume()
            else:
                # client has not queued anything and tried to press play
                pass
        
    async def connect(self, channel):
        if self.connected_client:
            if self.connected_client.is_connected():
                logging.warn('Player is already connected to channel {0.name}'.format(self.connected_client.channel))
                return
        self.connected_client = await channel.connect()
    
    async def disconnect(self):
        if self.connected_client.is_connected():
            await self.connected_client.disconnect()
        else:
            logging.warn('Player is not connected')
    
    def on_finished(self, error):
        self.messenger.gui['player'].embed = discord.Embed.from_dict({
                'title': 'Not Playing',
                'description': 'Nothing is playing. Send a youtube link to add a song.'
            })
        print('finished playing: ' + str(error))
        self.description = None
        self.read = 0
        future = asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.messenger.gui['player'].update)(), self.connected_client.loop)
        try:
            future.result()
        except:
            print('FUTURE Error')
    
    def on_read(self):
        self.read += 20
        # print(self.read)

    async def play_youtube(self, link):
        if self.connected_client.is_connected():
                # Check cache for hit
                print(link[-11:])
                database = self.cache.find_ytid(link[-11:])
                if database:
                    print('pass')
                else:
                    # if not grab info for streaming
                    with youtube_dlc.YoutubeDL(self.ydl_opts) as ydl:
                        video_info = ydl.extract_info(link, download=True)
                        source = video_info['formats'][0]['url']

                        self.description = video_info['description']

                        self.ChatEmbed.embed.description = video_info['description'][0:150] + '...'
                        self.ChatEmbed.embed.title = video_info['title']
                        self.ChatEmbed.embed.url = video_info['webpage_url']
                        self.ChatEmbed.embed.set_author(name = video_info['uploader'], url = video_info['uploader_url'])
                        self.ChatEmbed.embed.set_thumbnail(url = video_info['thumbnail'])
                        self.ChatEmbed.embed.set_footer(text= 'Source: Youtube', icon_url=YOUTUBE_ICON)
                        await self.ChatEmbed.update()

                        self.read = 0

                        audio: AudioSource = discord.FFmpegPCMAudio(executable=self.ffmpeg_path, source=source, **self.FFMPEG_OPTIONS)

                        if self.connected_client.is_playing():
                            self.connected_client.source = MusicSource(audio, self.on_read)
                        else:
                            self.connected_client.play(source = MusicSource(audio, self.on_read), after=self.on_finished)

        else:
            logging.error('Can\'t play_youtube() without connecting first')

    async def play_audio(self, audio: AudioSource):
        if self.connected_client.is_connected():
            if self.connected_client.is_playing():
                self.connected_client.source = MusicSource(audio, self.on_read)
            else:
                self.connected_client.play(source = MusicSource(audio, self.on_read), after=self.on_finished)