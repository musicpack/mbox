from discord.embeds import Embed, EmptyEmbed

from src.constants import USAGE_TEXT


class LyricsEmbed(Embed):
    """Represents a Lyrics object. Subclass of a player object."""
    def __init__(self, **kwargs) -> None:
        # Call super first so that it doesn't overwrite custom variables in this class
        super().__init__(**kwargs)
        
        self.title = 'Lyrics'
        
        # Footer Variables
        self.lyrics: str = kwargs.get('lyrics', None)
        self.lyrics_source: str = kwargs.get('lyrics_source', None)
        
        if not self.lyrics and not self.lyrics_source:
            self.description = USAGE_TEXT
            return

        if self.lyrics:
            self.description = self.lyrics[:2048] # TODO Support lyrics that are longer then the embed text limit in discord. (Page pagination?)
            if len(self.lyrics) > 2048:
                self.lyrics_source += ' [Discord message limit reached. Lyrics truncated.]'

        if self.lyrics_source:
            self.set_footer(text=self.lyrics_source)
        else:
            self.set_footer(text=EmptyEmbed)
