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
            self.max_description = 2048
            self.max_embed_field = 1024
            self.description = self.get_lyric()

                             
        if self.lyrics_source:
            self.set_footer(text=self.lyrics_source)
        else:
            self.set_footer(text=EmptyEmbed)
        
    
    def get_lyric(self) -> str:
        if(len(self.lyrics) < self.max_description):
            return self.lyrics

        description_lyric = ''
        embed_field_lyric = ''

        for verse in self.get_verses():
            if(len(description_lyric) + len(verse) >= self.max_description ):

                if(len(embed_field_lyric) + len(verse) >= self.max_embed_field ):
                    embed_field_lyric = embed_field_lyric + '\r\n\r\n' + verse
                    self.add_field(name='\u200B', value=embed_field_lyric, inline=False)

                else: 
                    embed_field_lyric = embed_field_lyric + '\r\n\r\n' + verse

            else: description_lyric = description_lyric + '\r\n\r\n' + verse           

        self.add_field(name='\u200B', value=embed_field_lyric, inline=False)
        return description_lyric


    def get_verses(self) -> list:
        return self.lyrics.split('\r\n\r\n')