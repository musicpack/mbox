import youtube_dl
import discord
import logging

class Player:
    def __init__(self, voice_channels, ffmpeg_path, playing = False, connected = False, connected_client = None) -> None:
        self.playing = playing
        self.connected = connected
        self.connected_client = None
        self.voice_channels = voice_channels

        self.ffmpeg_path = ffmpeg_path
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -ss 40'
        }
        self.ydl_opts = {'format': 'bestaudio'}
    
    async def connect(self, channel):
        if not self.connected:
            self.connected_client = await channel.connect()
            self.connected = True
        else:
            logging.warn('Player is already connected to channel {0.name}'.format(self.connected_client.channel))
    
    async def disconnect(self):
        if self.connected:
            await self.connected_client.disconnect()
            self.connected = False
        else:
            logging.warn('Player can\'t disconnect when not connected')

    async def play_youtube(self, link):
        if self.connected:
            if self.playing:
                with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                    source = ydl.extract_info(link, download=False)['formats'][0]['url']
                    self.connected_client.source = discord.FFmpegPCMAudio(executable=self.ffmpeg_path, source=source, **self.FFMPEG_OPTIONS)
                    self.playing = True
            else:
                def after(error):
                    self.playing = False

                with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                    source = ydl.extract_info(link, download=False)['formats'][0]['url']
                    self.connected_client.play(source = discord.FFmpegPCMAudio(executable=self.ffmpeg_path, source=source, **self.FFMPEG_OPTIONS), after=after)
                    self.playing = True

        else:
            logging.error('Can\'t play_youtube() without connecting first')
