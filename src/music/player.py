from discord.channel import VoiceChannel
from discord.player import AudioSource
import youtube_dl
import discord
import logging
import asyncio
import os
import threading
from src.commander.messenger import Messenger
from src.commander.element.Button import Button
from src.commander.element.ChatEmbed import ChatEmbed
from src.music.element.MusicSource import MusicSource
from src.music.element.MusicQueue import MusicQueue
from src.music.element.cache import Cache
from src.constants import *
from datetime import timedelta

class Player:
    def __init__(self, voice_channels, ffmpeg_path, messenger: Messenger) -> None:
        self.connected_client: discord.VoiceClient = None
        self.voice_channels = voice_channels
        self.messenger: Messenger = messenger
        self.client = self.messenger.client
        self.buttons = {
            'last_track': Button(emoji='⏮️', client = self.client, action=self.last),
            'play_pause': Button(emoji='⏯️', client = self.client, action=self.play_pause),
            'next_track': Button(emoji='⏭️', client = self.client, action=self.next),
            'lower_volume': Button(emoji='🔉', client = self.client, action=self.lower_volume),
            'raise_volume': Button(emoji='🔊', client = self.client, action=self.raise_volume),
            'toggle_description': Button(emoji='💬', client = self.client, action=self.toggle_description)
        }
        self.ChatEmbed : ChatEmbed = None
        self.cache = Cache()

        self.ffmpeg_path = ffmpeg_path
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
            ,'options': '-vn'
        }
        self.ydl_opts = {
            'format': 'bestaudio/worst'
        }

        self.description = None
        self.display = False
        self.playlist = None
        self.volume = 1.0
        self.last_voice_channel = None

        # self.footer = [] #TODO setup adaptive footer
    
    async def setup(self):
        self.ChatEmbed = self.messenger.gui['player']
        self.ChatEmbed.actions = list(self.buttons.values())
        self.ChatEmbed.embed.title = 'Not Playing'
        await self.ChatEmbed.update()

        self.playlist = MusicQueue(active_embed = self.messenger.gui['queue'], client = self.messenger.client)
        await self.playlist.setup()

        # @self.playlist.event
        # def on_remove_all():
        #     self.stop()

    async def lower_volume(self):
        if self.connected_client:
            if self.connected_client.is_connected():
                self.volume -= .16666666666
                self.connected_client.source.volume = self.volume

    async def raise_volume(self):
        if self.connected_client:
            if self.connected_client.is_connected():
                self.volume += .16666666666
                self.connected_client.source.volume = self.volume

    def stop(self):
        self.messenger.gui['player'].embed = discord.Embed.from_dict({
            'title': 'Not Playing',
            'description': 'Nothing is playing. Send a youtube link to add a song.'
        })
        asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.disconnect)(), self.client.loop)
        asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.messenger.gui['player'].update)(), self.client.loop)
        asyncio.run_coroutine_threadsafe(self.playlist.reset_all(), self.client.loop)
        return self.connected_client.stop()
    
    def pause(self):
        return self.connected_client.pause()

    def resume(self):
        return self.connected_client.resume()
    
    async def play(self, audio: MusicSource, channel: discord.VoiceChannel = None):
        if channel:
            await self.connect(channel)
        elif self.last_voice_channel:
            await self.connect(self.last_voice_channel)
        else:
            await self.connect(self.voice_channels[0])
        await self.connected_client.play(source = audio, after=self.on_finished)
    
    def last(self) -> MusicSource:
        try:
            music_source = self.playlist.prev()
        except IndexError:
            music_source = None
        if music_source:
            music_source.reset()
            if music_source.resolved:
                asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.update_embed_from_ytdict)(music_source.info, footer='Source: Youtube (cache)'), self.connected_client.loop)
            else:
                asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.update_embed_from_ytdict)(music_source.info, footer='Source: Youtube'), self.connected_client.loop)
            
            if self.connected_client:
                if self.connected_client.is_connected():
                    if self.connected_client.is_playing():
                        self.connected_client.source = music_source
                        return music_source
                    else:
                        self.connected_client.play(source = music_source, after=self.on_finished)
                        return music_source
                else:
                    asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.play)(music_source), self.client.loop)
                    return music_source
            else:
                asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.play)(music_source), self.client.loop)
                return music_source
        else:
            print('cant go back any further')
            return None
    
    def next(self) -> MusicSource:
        try:
            music_source = self.playlist.next()
        except IndexError:
            music_source = None
        if music_source:
            music_source.reset()

            if music_source.resolved:
                asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.update_embed_from_ytdict)(music_source.info, footer='Source: Youtube (cache)'), self.connected_client.loop)
            else:
                asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.update_embed_from_ytdict)(music_source.info, footer='Source: Youtube'), self.connected_client.loop)
                
            
            if self.connected_client:
                if self.connected_client.is_connected():
                    if self.connected_client.is_playing():
                        self.connected_client.source = music_source
                        return music_source
                    else:
                        self.connected_client.play(source = music_source, after=self.on_finished)
                        return music_source
                else:
                    asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.play)(music_source), self.client.loop)
                    return music_source
            else:
                asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.play)(music_source), self.client.loop)
                return music_source
        else:
            print('no music')
            self.stop()
            return None

    async def toggle_description(self):
        if self.description:
            if self.display:
                list_description = self.description.splitlines()
                self.ChatEmbed.embed.description = '\n'.join(list_description[0:3])
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

    async def connect(self, channel: VoiceChannel):
        if self.connected_client:
            if self.connected_client.is_connected():
                logging.warn('Player is already connected to channel {0.name}'.format(self.connected_client.channel))
                return
        self.connected_client = await channel.connect()
        await self.messenger.register_all()
        # await self.ChatEmbed.update(update_buttons=True)
        self.last_voice_channel = channel
        # self.volume = 1.0

    async def disconnect(self):
        if self.connected_client.is_connected():
            self.last_voice_channel = self.connected_client.channel
            await self.connected_client.disconnect()
        else:
            logging.warn('Player is not connected. Was it disconnected forcefully?')
        # await self.ChatEmbed.remove_buttons()
        await self.messenger.unregister_all()

    def on_finished(self, error):
        if error:
            logging.exception('error when finished playing: ',exc_info=error)
            self.stop()
        else:
            logging.info('finished playing')
            try:
                # TODO change race condiiton for main look to check if on_finished exec because of disconnect or next song
                self.next()
            except IndexError:
                pass

    def on_read(self, ms):
        # if ms % 7000 == 0:
        #     delta = timedelta(milliseconds=ms)
        #     self.ChatEmbed.embed.set_footer(text=str(delta))
        #     asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.ChatEmbed.update)(), self.connected_client.loop)
        pass

    async def play_youtube(self, link):
        if self.connected_client.is_connected():
                # Check cache for hit
                # print(link[-11:]) # TODO change id finding method
                # database = self.cache.find_ytid(link[-11:])
                
                database = False

                if database:
                    print('FOUND IN DATABASE')
                else:
                    # if not grab info to add for streaming queue
                    with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                        video_info = ydl.extract_info(link, download=False)
                        source = video_info['formats'][0]['url']

                        raw_audio_source: AudioSource = discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=source, **self.FFMPEG_OPTIONS)
                        audio = MusicSource(raw_audio_source, info = video_info, volume= self.volume)
                        self.playlist.add(audio)

                        if not self.connected_client.is_playing():
                            self.next()
                        
                        @audio.event
                        def on_read(ms):
                            self.on_read(ms)
                        
                        # Determine if video is cacheable
                        if not video_info['is_live']:
                            if video_info['filesize'] <= MAX_CACHESIZE: # TODO add handling when video_info['filesize'] is not found/supported
                                threading.Thread(target=lambda: audio.resolve(cache=True)).start()

                            else:
                                threading.Thread(target=lambda: audio.resolve(cache=False)).start()

                            @audio.event
                            def on_resolve(info, path):
                                if(self.playlist.current().info == info):
                                    self.ChatEmbed.embed.set_footer(text= 'Source: Youtube (file)', icon_url=YOUTUBE_ICON)
                                    asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.messenger.gui['player'].update)(), self.connected_client.loop)
                                    # TODO Remove all buttons
                            
        else:
            logging.error('Can\'t play_youtube() without connecting first')

    async def update_embed(self, *, title, title_url, description, author, author_url, author_thumbnail, thumbnail_url, footer, footer_thumbnail, truncate_description = True): 
        if title: self.ChatEmbed.embed.title = title
        if title_url: self.ChatEmbed.embed.url = title_url

        if description:
            if truncate_description:
                list_description = description.splitlines()
                self.ChatEmbed.embed.description = '\n'.join(list_description[0:3])
                self.display = False
            else:
                self.ChatEmbed.embed.description = self.description[0:2048]
                self.display = True
        
        if author: self.ChatEmbed.embed.set_author(name = author)
        if author_url: self.ChatEmbed.embed.set_author(url = author_url)
        if author_thumbnail: self.ChatEmbed.embed.set_author(icon_url = author_thumbnail)
        
        if thumbnail_url: self.ChatEmbed.embed.set_thumbnail(url = thumbnail_url)

        if footer: self.ChatEmbed.embed.set_footer(text= footer)
        if footer_thumbnail: self.ChatEmbed.embed.set_footer(icon_url=footer_thumbnail)

        # await self.ChatEmbed.update()

    async def play_audio(self, audio: AudioSource):
        if self.connected_client.is_connected():
            if self.connected_client.is_playing():
                self.connected_client.source = MusicSource(audio)
            else:
                self.connected_client.play(source = MusicSource(audio), after=self.on_finished)

    async def update_embed_from_ytdict(self, info: dict, truncate_description = True, footer = 'Source: Youtube'):
        self.description = info['description']
        list_description = info['description'].splitlines()

        self.ChatEmbed.embed.description = '\n'.join(list_description[0:3])
        self.ChatEmbed.embed.title = info['title']
        self.ChatEmbed.embed.url = info['webpage_url']
        self.ChatEmbed.embed.set_author(name = info['uploader'], url = info['uploader_url'])
        self.ChatEmbed.embed.set_thumbnail(url = info['thumbnail'])
        
        if footer:
            self.ChatEmbed.embed.set_footer(text= footer, icon_url=YOUTUBE_ICON)
        # await self.ChatEmbed.update()
