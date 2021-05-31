import logging
from discord import AudioSource
from discord import ClientException
import audioop
import os
import youtube_dl
from src.constants import SPONSORBLOCK_MUSIC_API
import discord
from src.music.element.cache import Cache
import requests
from datetime import timedelta
from config import DOWNLOAD_PATH, TEMP_PATH, FFMPEG_PATH

class MusicSource(AudioSource):
    """Transforms a previous :class:`AudioSource` to have volume controls.
    Also provides a callback function for the read function.
    Class derivation from PCMVolumeTransformer

    This does not work on audio sources that have :meth:`AudioSource.is_opus`
    set to ``True``.

    Parameters
    ------------
    original: :class:`AudioSource`
        The original AudioSource to transform.
    volume: :class:`float`
        The initial volume to set it to.
        See :attr:`volume` for more info.

    Raises
    -------
    TypeError
        Not an audio source.
    ClientException
        The audio source is opus encoded.
    """

    def __init__(self, original, info: dict, volume=1.0, resolved = False, sponsor_segments = [], skip_non_music = True):
        if not isinstance(original, AudioSource):
            raise TypeError('expected AudioSource not {0.__class__.__name__}.'.format(original))

        if original.is_opus():
            raise ClientException('AudioSource must not be Opus encoded.')

        self.original = original
        self.volume = volume

        self.amount_read = 0
        self.info: dict= info
        self.skip_non_music = skip_non_music
        self.sponsor_segments: list or None = sponsor_segments
        self.resolved: bool = resolved
        self.temp = False
        self.file_path = None

        self.resolve_non_music()
        
    @property
    def volume(self):
        """Retrieves or sets the volume as a floating point percentage (e.g. ``1.0`` for 100%)."""
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = max(value, 0.0)

    def cleanup(self):
        """Calls the original cleanup function and removes the downloaded file if it is marked as a temporary file"""
        self.original.cleanup()
        if self.temp:
            try:
                logging.debug('Removing temp file {0}'.format(self.file_path))
                os.remove(self.file_path)
            except PermissionError:
                logging.warn('Premission Error when removing {0}. Maybe the file is being used in other sessions?'.format(self.file_path))
            except Exception as e:
                logging.error(e)

    def read(self):

        if self.skip_non_music:
            while self.in_non_music():
                self.amount_read += 20
                ret = self.original.read()
                self.on_read(self.amount_read, True)

        self.amount_read += 20
        ret = self.original.read()
        self.on_read(self.amount_read, False)
        return audioop.mul(ret, 2, min(self._volume, 2.0))
    
    def in_non_music(self) -> bool:
        current_time = timedelta(milliseconds=self.amount_read)
        if self.sponsor_segments:
            for segment_response in self.sponsor_segments:
                segment_begin = timedelta(seconds = segment_response['segment'][0])
                segment_end = timedelta(seconds = segment_response['segment'][1])
                if segment_begin <= current_time and current_time < segment_end:
                    return True

        return False

    def reset(self):
        """Set the current audiosource back to 0:00"""
        custom_options = {'options': '-vn'}
        if self.amount_read > 0:
            if self.file_path:
                self.amount_read = 0
                self.original: AudioSource = discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=self.file_path, **custom_options)
            else:
                self.amount_read = 0
                self.original: AudioSource = discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=self.info['formats'][0]['url'], **custom_options)

    def resolve_non_music(self):
        """Finds non_music sections of the song if skip_non_music is true."""
        if self.skip_non_music:
            if not self.sponsor_segments:
                r = requests.get(SPONSORBLOCK_MUSIC_API.format(self.info['id']))
                if 'json' in r.headers.get('Content-Type'):
                    self.sponsor_segments = r.json()
                else:
                    self.sponsor_segments = None

    def resolve(self, cache=True):
        """Downloads song and sets it as the audiosource."""

        custom_opts = {
            'format': 'bestaudio',
            'writesubtitles': True,
            # 'writeautomaticsub': True,
            # 'allsubtitles': True,
            'progress_hooks': [self.on_download_state],
        }
        if cache:
            path = DOWNLOAD_PATH

        else:
            path = TEMP_PATH
            self.temp = True
        custom_opts['outtmpl'] = os.path.join(path, '%(title)s-%(id)s.%(ext)s')
        with youtube_dl.YoutubeDL(custom_opts) as ydl:
            ydl.process_ie_result(self.info, download=True)

    def on_download_state(self, d):
        if d['status'] == 'finished':
            path = os.path.abspath(d['filename'])
            filepath, file_extension = os.path.splitext(path)
            file_ytid = os.path.split(filepath)[-1].split('-')[-1]

            if file_extension == '.webm' or file_extension == '.m4a':
                custom_options = {'options': '-vn -ss ' + str(self.amount_read) + 'ms'}
                audio: AudioSource = discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=path, **custom_options)
                
                self.original = audio
                self.file_path = path
                self.resolved = True
                self.on_resolve(self.info, path)

    def event(self, event):
        """A decorator that registers an event to listen to.

          Events
        ---------
        on_read(ms_read: int)

        on_resolve(info: yt_dict, path: os.Path)
        """

        setattr(self, event.__name__, event)
        logging.debug('%s has successfully been registered as an event', event.__name__)
        return event
    
    def on_read(self, ms, non_music):
        """A placeholder event function intended to be overwritten"""
        pass

    def on_resolve(self, info, path):
        """A placeholder event function intended to be overwritten"""
        pass