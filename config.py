import os
import shutil
import configparser
import glob

def gen_config() -> configparser.ConfigParser:
    """Generates a default configeration file."""
    generated_config = configparser.ConfigParser()

    # [Default]
    generated_config.add_section('Default')
    generated_config['Default']['TOKEN'] = ''
    generated_config['Default']['FFMPEG_PATH'] = ''
    generated_config['Default']["GUILD_ID"] = ''

    # [Cache]
    generated_config.add_section('Cache')
    generated_config['Cache']['DOWNLOAD_PATH'] = os.path.join('cache', 'youtube')
    generated_config['Cache']['TEMP_PATH'] = os.path.join('cache', 'temp')
    generated_config['Cache']['MAX_CACHESIZE'] = '0'
    generated_config['Cache']['MAX_FILESIZE'] = '100000000'

    return generated_config

# config specific functions
def write_config(config: configparser.ConfigParser) -> None:
    with open("config.ini", 'w') as f:
        config.write(f)

def set_token(config: configparser.ConfigParser):
    """sets the token dynamically"""
    config_token = config['Default']['TOKEN']
    envvar_token = os.environ.get('DiscordToken_mbox')
    
    if config_token:
        return config_token
    elif envvar_token:
        return envvar_token
    else:
       return input("No token in config file or in enviroment variable \'DiscordToken_mbox\'. Please generate a token and enter it below.")

def set_ffmpeg_path(config: configparser.ConfigParser):
    """sets the ffmpeg_path dynamically"""
    try:
        if config['Default']['FFMPEG_PATH']:
            return config['Default']['FFMPEG_PATH']
        elif shutil.which('ffmpeg'):
            return 'ffmpeg'
        elif glob.glob('ffmpeg*'):
            return get_ffmpeg_path(glob.glob('ffmpeg*'))
    except:
        FFMPEG_ERROR_NOT_FOUND = "ffmpeg was not found on this system. If installed, provide the path in the config."
        raise ProcessLookupError(FFMPEG_ERROR_NOT_FOUND)

def set_guild_id(config: configparser.ConfigParser) -> list[int]:
    """sets the ffmpeg_path dynamically"""
    config_guild_id = config['Default']['GUILD_ID']
    envar_guild_id = os.getenv("DISCORD_GUILD", "")
    if config_guild_id:
        return [int(config_guild_id)]
    elif envar_guild_id:
        return [int(envar_guild_id)]
    else:
        return None

def get_ffmpeg_path(ffmpeg_paths: str) -> str:
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

# generate and set the config
default_config = gen_config()
if not os.path.isfile('config.ini'):
    write_config(default_config)
else:
    disk_config = configparser.ConfigParser()
    disk_config.read('config.ini')

    # find missing fields in disk config add them if missing
    reference_dict: dict = default_config._sections
    disk_dict: dict = disk_config._sections

    section: str
    section_dict: dict
    for section, section_dict in reference_dict.items():
        # check disk dictionary has the section
        if not disk_dict[section]:
            disk_config.add_section(section)

        key: str
        value: str
        for key, value in section_dict.items():
            # check disk dictionary have a key in the section
            if key not in disk_dict[section]: 
                disk_config[section][key] = default_config[section][key]
                write_config(disk_config) # write changes to disk

###### USER CONFIG ######
TOKEN = set_token(disk_config)
FFMPEG_PATH = set_ffmpeg_path(disk_config)
GUILD_ID= set_guild_id(disk_config)

# TODO: Sanitize and check if values are valid
DOWNLOAD_PATH = disk_config['Cache']['DOWNLOAD_PATH']
TEMP_PATH = disk_config['Cache']['TEMP_PATH']
MAX_CACHESIZE = int(disk_config['Cache']['MAX_CACHESIZE'])
MAX_FILESIZE = int(disk_config['Cache']['MAX_FILESIZE'])

