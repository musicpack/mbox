from discord.embeds import Embed

from src.constants import VERSION


class ReporterEmbed(Embed):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.title = f'Music Box {VERSION}'
        self.description = "\n**Please mute this channel to avoid notification spam!**" + \
                           "\n**NEW!!** Try slash commands `/play`" + \
                           "\n*Early Access, please report any bugs!*" + \
                           "\n[Help](https://github.com/borisliao/mbox/wiki/Help) | [Changelog](https://github.com/borisliao/mbox/blob/master/CHANGELOG.md) | [About](https://github.com/borisliao/mbox)\n"
