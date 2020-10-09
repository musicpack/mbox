import youtube_dl
import discord

class Player:
    def __init__(self) -> None:
        playing = False
        
async def play_youtube(channel, link):
    # with youtube_dl.YoutubeDL() as ydl:
    #     song_info = ydl.extract_info("https://www.youtube.com/watch?v=MwxgUVrj5m4", download=False)
    #     voice_client.play(discord.FFmpegPCMAudio(executable="C:/Users/bliao/Desktop/mbox/ffmpeg-2020-09-30-git-9d8f9b2e40-full_build/bin/ffmpeg.exe", source=song_info["formats"][0]["url"], before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'"))
    #     voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
    #     voice_client.source.volume = 1'https://www.youtube.com/watch?v=68-5opzvdUc'
    voice_client = await channel.connect()
    ffmpeg_path = 'C:/Users/bliao/Desktop/mbox/ffmpeg-2020-09-30-git-9d8f9b2e40-full_build/bin/ffmpeg.exe'
    ydl_opts = {'format': 'bestaudio'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        source = ydl.extract_info(link, download=False)['formats'][0]['url']
        voice_client.play(discord.FFmpegPCMAudio(executable=ffmpeg_path, source=source, **FFMPEG_OPTIONS))
