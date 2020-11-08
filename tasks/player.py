import youtube_dl
import discord
import logging
from tasks.commander.messenger import Messenger

class Player:
    def __init__(self, voice_channels, ffmpeg_path, messenger: Messenger) -> None:
        self.connected_client: discord.VoiceClient = None
        self.voice_channels = voice_channels
        self.messenger: Messenger = messenger
        self.playlist = []

        self.ffmpeg_path = ffmpeg_path
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -ss 40'
        }
        self.ydl_opts = {'format': 'bestaudio'}
    
    def stop(self):
        return self.connected_client.stop()
    
    def pause(self):
        return self.connected_client.pause()

    def resume(self):
        return self.connected_client.resume()
    
    async def connect(self, channel):
        if not self.connected_client or not self.connected_client.is_connected():
            self.connected_client = await channel.connect()
        else:
            logging.warn('Player is already connected to channel {0.name}'.format(self.connected_client.channel))
    
    async def disconnect(self):
        if self.connected_client.is_connected():
            await self.connected_client.disconnect()
        else:
            logging.warn('Player is not connected')
    
    def on_finished(self, error):
        print('finished playing: ' + str(error))

    async def play_youtube(self, link):
        if self.connected_client.is_connected():
                with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                    video_info = ydl.extract_info(link, download=False)
                    source = video_info['formats'][0]['url']
                    self.messenger.gui['player'].embed.title = video_info['title']
                    await self.messenger.gui['player'].update()

                    if self.connected_client.is_playing():
                        self.connected_client.source = discord.FFmpegPCMAudio(executable=self.ffmpeg_path, source=source, **self.FFMPEG_OPTIONS)
                    else:
                        self.connected_client.play(source = discord.FFmpegPCMAudio(executable=self.ffmpeg_path, source=source, **self.FFMPEG_OPTIONS), after=self.on_finished)

        else:
            logging.error('Can\'t play_youtube() without connecting first')
