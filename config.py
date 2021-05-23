import os
import shutil
import configparser
import glob

#Config specific variables
__config = configparser.ConfigParser()
_FFMPEG_ERROR_NOT_FOUND = "ffmpeg was not found on this system. If installed, provide the path in the config."

# config specific functions
def make_config():
    """Generates a default configeration file."""
    __config.add_section('Default')
    __config['Default']['TOKEN'] = ''
    __config['Default']['FFMPEG_PATH'] = ''
    __config['Default']["GUILD_ID"] = ''
    __config.add_section('Cache')
    __config['Cache']['DOWNLOAD_PATH'] = os.path.join('cache', 'youtube')
    __config['Cache']['TEMP_PATH'] = os.path.join('cache', 'temp')
    __config['Cache']['MAX_CACHESIZE'] = '0'
    __config['Cache']['MAX_FILESIZE'] = '100000000'
    with open("config.ini", 'w') as f:
        __config.write(f)

#sets the token dynamically
def set_token():
    config_token = __config['Default']['TOKEN']
    envvar_token = os.environ.get('DiscordToken_mbox')
    if config_token:
        return  config_token
    elif envvar_token:
        return envvar_token
    else:
       return  input("No token in config file or in enviroment variable \'DiscordToken_mbox\'. Please generate a token and enter it below. ")

#sets the ffmpeg_path dynamically
def set_ffmpeg_path():
    try:
        if __config['Default']['FFMPEG_PATH']:
            return __config['Default']['FFMPEG_PATH']
        elif shutil.which('ffmpeg'):
            return 'ffmpeg'
        elif glob.glob('ffmpeg*'):
            return get_ffmpeg_path(glob.glob('ffmpeg*'))
    except:
        raise ProcessLookupError(_FFMPEG_ERROR_NOT_FOUND)

def set_guild_id():
    config_guild_id = __config['Default']['GUILD_ID']
    envar_guild_id = os.getenv("DISCORD_GUILD", "")
    if config_guild_id:
        return int(config_guild_id)
    elif envar_guild_id:
        return int(envar_guild_id)
    else:
        return int(input("Please set your guild-id "))


def get_ffmpeg_path(ffmpeg_paths: str):
    for path in ffmpeg_paths:
        if os.path.isdir(path):
            try:
                if os.name == 'posix':
                    return shutil.which(os.path.join(path,'ffmpeg'))
                elif os.name == 'nt':
                    return shutil.which(os.path.join(path,'bin','ffmpeg.exe'))
            except Exception:
                raise FileNotFoundError

        # if ffmpeg on the root folder is a binary file, assign it as the ffmpeg path
        elif os.path.isfile(path) and os.name == 'posix':
            try:
                return shutil.which('./ffmpeg')
            except:
                raise FileNotFoundError

# create and set the config
if not os.path.isfile('config.ini'):
    make_config()
__config.read('config.ini')

###### USER CONFIG ######
TOKEN = set_token()
FFMPEG_PATH = set_ffmpeg_path()
GUILD_ID= set_guild_id()


# TODO: Sanitize and check if values are valid
DOWNLOAD_PATH = __config['Cache']['DOWNLOAD_PATH']
TEMP_PATH = __config['Cache']['TEMP_PATH']
MAX_CACHESIZE = int(__config['Cache']['MAX_CACHESIZE'])
MAX_FILESIZE = int(__config['Cache']['MAX_FILESIZE'])

