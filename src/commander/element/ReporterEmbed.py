from discord.embeds import Embed

from src.constants import VERSION


class ReporterEmbed(Embed):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.title = f"Music Box {VERSION}"
        self.description = (
            "\n**Please mute this channel to avoid notification spam!**"
            + "\nWelcome, [music bot refugees!](https://www.theverge.com/2021/9/12/22669502/youtube-discord-rythm-music-bot-closure)."
            + "\nTry `/play` or just send your youtube link in this channel."
            + "\n**NEW in 0.7** Radio Mode `/radio`"
            + "\n*Early Access, please report any bugs!*"
            + "\n[Help](https://github.com/borisliao/mbox/wiki/Help) | [Changelog](https://github.com/borisliao/mbox/blob/master/CHANGELOG.md) | [About](https://github.com/borisliao/mbox)\n"
        )

    def __eq__(self, o: object) -> bool:
        def ordered_eval():
            yield self.description == o.description
            yield self.title == o.title

        return all(ordered_eval()) if type(o) == ReporterEmbed else False
