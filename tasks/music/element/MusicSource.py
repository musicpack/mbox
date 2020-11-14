from discord import AudioSource
from discord import ClientException
import audioop

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

    def __init__(self, original, readCB, volume=1.0, name = None):
        if not isinstance(original, AudioSource):
            raise TypeError('expected AudioSource not {0.__class__.__name__}.'.format(original))

        if original.is_opus():
            raise ClientException('AudioSource must not be Opus encoded.')

        self.original = original
        self.volume = volume
        self.readCB = readCB
        self.name = name

    @property
    def volume(self):
        """Retrieves or sets the volume as a floating point percentage (e.g. ``1.0`` for 100%)."""
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = max(value, 0.0)

    def cleanup(self):
        self.original.cleanup()

    def read(self):
        self.readCB()
        ret = self.original.read()
        return audioop.mul(ret, 2, min(self._volume, 2.0))