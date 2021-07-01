from discord.embeds import Embed

from src.commander.element.LyricsEmbed import LyricsEmbed
from src.commander.element.PlayerEmbed import PlayerEmbed
from src.commander.element.QueueEmbed import QueueEmbed
from src.commander.element.ReporterEmbed import ReporterEmbed


class EmbedFactory:
    def create_embed(embed_type: str, **kwargs) -> Embed:
        if embed_type == "reporter":
            return ReporterEmbed(**kwargs)
        elif embed_type == "lyrics":
            return LyricsEmbed(**kwargs)
        elif embed_type == "queue":
            return QueueEmbed(**kwargs)
        elif embed_type == "player":
            return PlayerEmbed(**kwargs)
