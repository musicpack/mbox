import os
import configparser
import shutil
import glob

###### PROGRAM CONSTANTS ######
VERSION = '0.5'
YOUTUBE_ICON = 'https://yt3.ggpht.com/a/AATXAJxHHP_h8bUovc1qC4c07sVXxVbp3gwDEg-iq8gbFQ=s100-c-k-c0xffffffff-no-rj-mo'
USAGE_TEXT = 'Send a search phrase or a link to play a song!'
CONFIG_PATH = 'config.ini'
SPONSORBLOCK_MUSIC_API = 'https://sponsor.ajay.app/api/skipSegments?videoID={0}&category=music_offtopic'
__config = configparser.ConfigParser()

##### CONFIG F

def generate_config():
    """Generates a default configeration file."""
    __config.add_section('Default')
    __config['Default']['TOKEN'] = ''
    __config['Default']['FFMPEG_PATH'] = 'ffmpeg/ffmpeg'
    __config.add_section('Cache')
    __config['Cache']['DOWNLOAD_PATH'] = os.path.join('cache', 'youtube')
    __config['Cache']['TEMP_PATH'] = os.path.join('cache', 'temp')
    __config['Cache']['MAX_CACHESIZE'] = '0'
    __config['Cache']['MAX_FILESIZE'] = '100000000'
    with open(CONFIG_PATH, 'w') as f:
        __config.write(f)

if not os.path.isfile(CONFIG_PATH):
    generate_config()

__config.read(CONFIG_PATH)

###### USER CONFIG ######
__config_token = __config['Default']['TOKEN']
__envvar_token = os.environ.get('DiscordToken_mbox')
if __config_token:
    TOKEN = __config_token
elif __envvar_token:
    TOKEN = __envvar_token
else:
    print('No token in config file or in enviroment variable \'DiscordToken_mbox\'. Please generate a token and enter it below.')
    print('token',end=': ')
    TOKEN = input()
    os.environ['DiscordToken_mbox'] = TOKEN

__config_ffmpeg_path = __config['Default']['FFMPEG_PATH']
__glob_results = glob.glob('ffmpeg*')
if __config_ffmpeg_path:
    FFMPEG_PATH = __config_ffmpeg_path
elif shutil.which('ffmpeg'):
    FFMPEG_PATH = 'ffmpeg'
elif __glob_results:
    for result in __glob_results:
        if os.path.isdir(result):
            posix_path = shutil.which(os.path.join(result,'ffmpeg'))
            windows_path = shutil.which(os.path.join(result,'bin','ffmpeg.exe'))
            if posix_path and os.name == 'posix':
                FFMPEG_PATH = posix_path
                break
            elif windows_path and os.name == 'nt':
                FFMPEG_PATH = windows_path
                break
else:
    raise ProcessLookupError('ffmpeg was not found on this system. If installed, provide the path in the config.')

# TODO: Sanitize and check if values are valid
DOWNLOAD_PATH = __config['Cache']['DOWNLOAD_PATH']
TEMP_PATH = __config['Cache']['TEMP_PATH']
MAX_CACHESIZE = int(__config['Cache']['MAX_CACHESIZE'])
MAX_FILESIZE = int(__config['Cache']['MAX_FILESIZE'])
