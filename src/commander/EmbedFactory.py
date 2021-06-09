from discord.embeds import Embed

from src.commander.element.PlayerEmbed import PlayerEmbed
from src.commander.element.QueueEmbed import QueueEmbed
from src.commander.element.LyricsEmbed import LyricsEmbed
from src.commander.element.ReporterEmbed import ReporterEmbed


class EmbedFactory:
    def create_embed(type: str, **kwargs) -> Embed:
        if type == 'reporter':
            return ReporterEmbed(**kwargs)
        elif type == 'lyrics':
            return LyricsEmbed(**kwargs)
        elif type == 'queue':
            return QueueEmbed(**kwargs)
        elif type == 'player':
            return PlayerEmbed(**kwargs)
