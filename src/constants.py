import os

VERSION = '0.1'
YOUTUBE_ICON = 'https://yt3.ggpht.com/a/AATXAJxHHP_h8bUovc1qC4c07sVXxVbp3gwDEg-iq8gbFQ=s100-c-k-c0xffffffff-no-rj-mo'
DOWNLOAD_PATH = os.path.join('cache', 'youtube')
TEMP_PATH = os.path.join('cache', 'temp')
MAX_CACHESIZE = 0 # in bytes, default 10 MB
MAX_FILESIZE = 100000000 # in bytes, default 100 MB

FFMPEG_PATH ='C:/Users/bliao/Desktop/mbox/ffmpeg-2020-09-30-git-9d8f9b2e40-full_build/bin/ffmpeg.exe'
TOKEN = os.environ.get('DiscordToken_mbox')