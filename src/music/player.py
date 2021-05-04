import threading
from discord.channel import VoiceChannel
from discord.player import AudioSource
import youtube_dl
import discord
import logging
import asyncio

from src.commander.messenger import Messenger
from src.commander.element.Button import Button
from src.commander.element.ChatEmbed import ChatEmbed
from src.music.element.MusicSource import MusicSource
from src.music.element.MusicQueue import MusicQueue
from src.music.element.cache import Cache
from src.music.element.Lyrics import Lyrics
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
        self.volume = 50
        self.last_voice_channel = None
        self.timeline = timedelta(seconds=0)
        self.paused = True
        self.ms_displayed = 0
        self.lyrics: Lyrics = None

        self.footer = {
            'icon_url': None,
            'paused': None,
            'source': None,
            'track': None,
            'volume': self.get_volume(),
            'timeline': self.get_timeline(),
            'sponsorblock': None
            }
    
    async def setup(self):
        self.ChatEmbed = self.messenger.gui['player']
        self.ChatEmbed.actions = list(self.buttons.values())
        self.ChatEmbed.embed.title = 'Not Playing'
        await self.ChatEmbed.update()

        self.playlist = MusicQueue(active_embed = self.messenger.gui['queue'], client = self.messenger.client)
        await self.playlist.setup()

        # initilization of variable happens here because messenger is not ready to provide this
        # by the time this player class has be inilizied
        self.lyrics = self.messenger.gui['lyrics']
        # @self.playlist.event
        # def on_remove_all():
        #     self.stop()

    async def lower_volume(self):
        if self.connected_client:
            if self.connected_client.is_connected():
                if not self.volume <= 0:
                    self.volume -= 10
                    self.connected_client.source.volume = self.volume/100
                    self.add_to_footer(volume=self.get_volume())
                    await self.ChatEmbed.update()

    async def raise_volume(self):
        if self.connected_client:
            if self.connected_client.is_connected():
                if not self.volume >= 200:
                    self.volume += 10
                    self.connected_client.source.volume = self.volume/100
                    self.add_to_footer(volume=self.get_volume())
                    await self.ChatEmbed.update()

    def stop(self):
        if self.connected_client:
            self.connected_client.stop()

            if self.connected_client.is_connected():
                asyncio.run_coroutine_threadsafe(self.disconnect(), self.client.loop)
        
        self.messenger.gui['player'].embed = discord.Embed.from_dict({
            'title': 'Not Playing',
            'description': 'Nothing is playing. ' + USAGE_TEXT
        })
        self.paused = True
        asyncio.run_coroutine_threadsafe(self.messenger.gui['player'].update(), self.client.loop)
        asyncio.run_coroutine_threadsafe(self.playlist.reset_all(), self.client.loop)
        asyncio.run_coroutine_threadsafe(self.lyrics.reset(), self.client.loop)
    
    def pause(self):
        self.paused = True
        self.update_footer_text()
        return self.connected_client.pause()

    def resume(self):
        self.paused = False
        self.update_footer_text()
        return self.connected_client.resume()
    
    async def play(self, audio: MusicSource, channel: discord.VoiceChannel = None):
        if channel:
            await self.connect(channel)
        elif self.last_voice_channel:
            await self.connect(self.last_voice_channel)
        else:
            await self.connect(self.voice_channels[0])
        await self.connected_client.play(source = audio, after=self.on_finished)
    
    # TODO: Simplify the last, next, stop functions of the player to use the same function to update the gui's
    def last(self) -> MusicSource:
        self.timeline = timedelta(seconds=0)
        self.footer['sponsorblock'] = None
        self.ms_displayed = -1
        try:
            music_source = self.playlist.prev()
        except IndexError:
            music_source = None
        if music_source:
            asyncio.run_coroutine_threadsafe(self.lyrics.update_lyrics(music_source.info['id']), self.client.loop)
            music_source.reset()
            if music_source.resolved:
                asyncio.run_coroutine_threadsafe(self.update_embed_from_ytdict(music_source.info, footer='Youtube 🗃️'), self.connected_client.loop)
            else:
                asyncio.run_coroutine_threadsafe(self.update_embed_from_ytdict(music_source.info, footer='Youtube'), self.connected_client.loop)
            
            if self.connected_client:
                if self.connected_client.is_connected():
                    if self.connected_client.is_playing():
                        self.connected_client.source = music_source
                    else:
                        self.connected_client.play(source = music_source, after=self.on_finished)
                        
                    return music_source
                
            asyncio.run_coroutine_threadsafe(self.play(music_source), self.client.loop)
            return music_source
        else:
            print('cant go back any further')
            return None
    
    def next(self) -> MusicSource:
        self.timeline = timedelta(seconds=0)
        self.footer['sponsorblock'] = None
        self.ms_displayed = -1
        try:
            music_source = self.playlist.next()
        except IndexError:
            music_source = None

        if music_source:
            asyncio.run_coroutine_threadsafe(self.lyrics.update_lyrics(music_source.info['id']), self.client.loop)
            music_source.reset()

            footer_text = 'Youtube'
            if music_source.resolved:
                footer_text += ' 🗃️'
            self.paused = False
            self.update_footer_text()
            asyncio.run_coroutine_threadsafe(self.update_embed_from_ytdict(music_source.info, footer=footer_text), self.connected_client.loop)
            
            if self.connected_client:
                if self.connected_client.is_connected():
                    if self.connected_client.is_playing():
                        self.connected_client.source = music_source
                    else:
                        self.connected_client.play(source = music_source, after=self.on_finished)
                else:
                    asyncio.run_coroutine_threadsafe(self.play(music_source), self.client.loop)
            else:
                asyncio.run_coroutine_threadsafe(self.play(music_source), self.client.loop)
            return music_source
        else:
            logging.info('No more music to play. Stopping...')
            self.stop()
            return None

    async def toggle_description(self):
        if self.description:
            if self.display:
                list_description = self.description.splitlines()
                self.ChatEmbed.embed.description = '\n'.join(list_description[0:3])
                self.display = False
                self.update_footer_text()
                await self.ChatEmbed.update()
            else:
                # TODO: Make button toggle multipage instead of just 2 pages 
                self.ChatEmbed.embed.description = self.description[0:2048]
                self.display = True
                self.update_footer_text()
                await self.ChatEmbed.update()

    async def play_pause(self):
        if self.connected_client:
            if self.connected_client.is_playing():
                self.pause()
                await self.ChatEmbed.update()
            elif self.connected_client.is_paused():
                self.resume()
                await self.ChatEmbed.update()
            else:
                # client has not queued anything and tried to press play
                pass

    async def connect(self, channel: VoiceChannel):
        if self.connected_client:
            if self.connected_client.is_connected():
                logging.warn('Player is already connected to channel {0.name}'.format(self.connected_client.channel))
                return
        self.clear_footer()
        self.connected_client = await channel.connect()
        # Function is ran in async so that buttons can register while the player is free to do other things
        # Be aware that this might mask errors in that function 
        asyncio.run_coroutine_threadsafe(self.messenger.register_all(), self.client.loop)
        self.last_voice_channel = channel

    async def disconnect(self):
        if self.connected_client.is_connected():
            self.last_voice_channel = self.connected_client.channel
            await self.connected_client.disconnect()
        else:
            logging.warn('Player is not connected. Was it disconnected forcefully?')
        # Function is ran in async so that buttons can register while the player is free to do other things
        # Be aware that this might mask errors in that function 
        asyncio.run_coroutine_threadsafe(self.messenger.unregister_all(), self.client.loop)

    def on_finished(self, error):
        if error:
            logging.exception('Error when finished playing: ',exc_info=error)
            self.stop()
        else:
            logging.debug('Finished playing song')
            self.timeline = None
            try:
                # TODO change race condiiton for main look to check if on_finished exec because of disconnect or next song
                self.next()
            except IndexError:
                pass

    def on_read(self, ms, non_music):
        self.timeline = timedelta(milliseconds=ms)
        if non_music:
            self.add_to_footer(sponsorblock='✔️Skipped Non Music')
            self.ms_displayed = 14000
        if self.ms_displayed > 0:
            self.ms_displayed -= 20
        if (ms % 14000 == 0 and not non_music) or self.ms_displayed == 13960: # 13960 represents the point where ms_displayed starts decrementing
            if self.ms_displayed == 0:
                self.footer['sponsorblock'] = None
                self.ms_displayed = -1 # make negative to avoid line above assignment multiple times
            self.update_footer_text()
            asyncio.run_coroutine_threadsafe(self.ChatEmbed.update(), self.connected_client.loop)
        pass

    async def play_youtube(self, link: str):
        if self.connected_client.is_connected():
                # TODO: Fix so that this function does not need to regex find the youtube id again
                #       The parser calling this function already has the youtube id.

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

                        raw_audio_source = discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=source, **self.FFMPEG_OPTIONS)
                        audio = MusicSource(raw_audio_source, info = video_info, volume= self.volume/100)
                        self.playlist.add(audio)

                        # If the player is not playing because it just came in to the channel (not because of being paused), advance the track head to the next (just added) song
                        if not self.connected_client.is_playing():
                            if not self.connected_client.is_paused():
                                self.next()
                        
                        @audio.event
                        def on_read(ms, non_music):
                            self.on_read(ms, non_music)
                        
                        # Determine if video is cacheable
                        if not video_info['is_live']: # TODO Player should show that the video is live in the GUI
                            if video_info['filesize']: # TODO add handling when video_info['filesize'] is not found/supported
                                do_cache = True if video_info['filesize'] <= MAX_CACHESIZE else False
                                threading.Thread(target=lambda: audio.resolve(cache=do_cache)).start()

                            @audio.event
                            def on_resolve(info, path):
                                if(self.playlist.current().info == info): # TODO: fix if client skips song/video before finished downloading, current() will be None
                                    self.add_to_footer(source= 'Youtube 📁', icon_url=YOUTUBE_ICON)
                                    asyncio.run_coroutine_threadsafe(self.messenger.gui['player'].update(), self.connected_client.loop)
                            
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

        await self.ChatEmbed.update()

    async def play_audio(self, audio: AudioSource):
        if self.connected_client.is_connected():
            if self.connected_client.is_playing():
                self.connected_client.source = MusicSource(audio)
            else:
                self.connected_client.play(source = MusicSource(audio), after=self.on_finished)

    async def update_embed_from_ytdict(self, info: dict, footer = 'Youtube'):
        self.description = info['description']
        list_description = info['description'].splitlines()

        self.ChatEmbed.embed.description = '\n'.join(list_description[0:3])
        self.ChatEmbed.embed.title = info['title']
        self.ChatEmbed.embed.url = info['webpage_url']
        self.ChatEmbed.embed.set_author(name = info['uploader'], url = info['uploader_url'])
        self.ChatEmbed.embed.set_thumbnail(url = info['thumbnail'])
        
        if footer:
            self.add_to_footer(source= footer, icon_url=YOUTUBE_ICON)
        await self.ChatEmbed.update()

    ########### FOOTER ############

    def add_to_footer(self, *, paused = None, icon_url=None, source = None, track=None, volume=None, timeline=None, sponsorblock = None):
        """Add info to footer and updates the footer in ChatEmbed. Does not send the ChatEmbed."""
        if (paused): self.footer['paused'] = paused
        if (icon_url): self.footer['icon_url'] = icon_url
        if (source): self.footer['source'] = source
        if (track): self.footer['track'] = track
        if (volume): self.footer['volume'] = volume
        if (timeline): self.footer['timeline'] = timeline
        if (sponsorblock): self.footer['sponsorblock'] = sponsorblock

        self.update_footer_text()
    
    def update_footer_text(self):
        """Generates new text and updates the footer text in chatEmbed. Generates paused, volume, timeline states."""
        footer_text = self.generate_footer_text()

        self.ChatEmbed.embed.set_footer(text= footer_text, icon_url=self.footer['icon_url'])
    
    def generate_footer_text(self):
        """Generates footer text based on current infomation. Generates paused, volume, timeline states."""
        self.footer['paused'] = self.get_paused()
        self.footer['volume'] = self.get_volume()
        self.footer['timeline'] = self.get_timeline()

        footer_list = []
        for value in list(self.footer.values())[1:]:
            if value:
                footer_list.append(value)
        return ' | '.join(footer_list)

    def clear_footer(self):
        """Clears the footer text internally and in the ChatEmbed. Does not send the ChatEmbed"""
        self.footer = {
            'icon_url': None,
            'paused': None,
            'source': None,
            'track': None,
            'volume': self.get_volume(),
            'timeline': self.get_timeline(),
            'sponsorblock': None
        }
        self.ChatEmbed.embed.set_footer()
    
    def get_volume(self):
        """Gets a string formated volume value. Primarly for footer text."""
        emoji = '🔊'
        if self.volume <= 0:
            emoji = '🔇'
        elif self.volume <= 30:
            emoji = '🔈'
        elif self.volume <= 70:
            emoji = '🔉'
        else:
            emoji = '🔊'

        # TODO: Fix volume string when negative
        return emoji + str(self.volume/100)[:3] if self.volume != None else None
    
    def get_timeline(self):
        """Gets a string formated timeline/length value. Primarly for footer text."""
        duration = ''
        if self.playlist:
            current_playing = self.playlist.current()
            if current_playing:
                duration = timedelta(seconds=current_playing.info['duration'])
            else:
                return None

            if self.timeline != None:
                current = str(self.timeline)[:7]
                total = str(duration)[:7]
                if total[:2] == '0:':
                    current = current[2:]
                    total = total[2:]
                if total[:1] == '0':
                    current = current[1:]
                    total = total[1:]
                return current + '/' +  total
            else:
                return None
        else:
            return None

    def get_paused(self):
        """Gets a string formated paused value. Primarly for footer text."""

        return 'PAUSED' if self.paused else None