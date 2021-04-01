import logging
from discord import AudioSource
from discord import ClientException
import audioop
import os
import youtube_dl
from src.constants import *
import discord
from src.music.element.cache import Cache

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

    def __init__(self, original, info: dict, volume=1.0, resolved = False):
        if not isinstance(original, AudioSource):
            raise TypeError('expected AudioSource not {0.__class__.__name__}.'.format(original))

        if original.is_opus():
            raise ClientException('AudioSource must not be Opus encoded.')

        self.original = original
        self.volume = volume

        self.amount_read = 0
        self.info: dict= info
        self.resolved: bool = resolved
        self.temp = False
        self.file_path = None

    @property
    def volume(self):
        """Retrieves or sets the volume as a floating point percentage (e.g. ``1.0`` for 100%)."""
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = max(value, 0.0)

    def cleanup(self):
        self.original.cleanup()
        if self.temp:
            try:
                os.remove(self.file_path)
            except PermissionError:
                logging.warn('Premission Error when removing {0}. Maybe the file is being used in other sessions?'.format(self.file_path))
            except Exception as e:
                logging.error(e)

    def read(self):
        self.amount_read += 20
        self.on_read(self.amount_read)

        ret = self.original.read()
        return audioop.mul(ret, 2, min(self._volume, 2.0))

    def reset(self):
        custom_options = {'options': '-vn'}
        if self.amount_read > 0:
            if self.file_path:
                self.amount_read = 0
                self.original: AudioSource = discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=self.file_path, **custom_options)
            else:
                self.amount_read = 0
                self.original: AudioSource = discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=self.info['formats'][0]['url'], **custom_options)

    def resolve(self, cache=True):
        custom_opts = {
            'format': 'bestaudio',
            'writesubtitles': True,
            'writeautomaticsub': True,
            # 'allsubtitles': True,
            'progress_hooks': [self.on_download_state],
        }
        if cache:
            custom_opts['outtmpl'] = os.path.join(DOWNLOAD_PATH, '%(title)s-%(id)s.%(ext)s')
            with youtube_dl.YoutubeDL(custom_opts) as ydl:
                ydl.process_ie_result(self.info, download=True)
        else:
            self.temp = True
            custom_opts['outtmpl'] = os.path.join(TEMP_PATH, '%(title)s-%(id)s.%(ext)s')
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
    
    def on_read(self, ms):
        pass

    def on_resolve(self, info, path):
        pass