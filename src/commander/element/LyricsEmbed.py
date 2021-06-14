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
            lyric = ''
            lyric_text = ''
            lyric_list = self.lyrics.split('\r\n\r\n')
            
            #Lyric with gaps
            if(len(lyric_list) > 1):
                for lyric_line in lyric_list:
                    if(lyric_text == ''):
                        if(len(lyric) + len(lyric_line) < 2048 ):
                            lyric = lyric + '\r\n\r\n' + lyric_line
                        else:
                            self.description = lyric
                            lyric_text = lyric_line
                    else:
                        if(len(lyric_text) + len(lyric_line) < 1024 ):
                            lyric_text = lyric_text + '\r\n\r\n' + lyric_line
                        else:
                            self.add_field(name='\u200B', value=lyric_text, inline=False)
                            lyric_text = lyric_line

            #Lyric without gap
            elif(len(lyric_list) == 1):
                lyric_list = self.lyrics.split('\r\n')
                for lyric_line in lyric_list:
                    if(lyric_text == ''):
                        if(len(lyric) + len(lyric_line) < 2048 ):
                            lyric = lyric + '\r\n' + lyric_line
                        else:
                            self.description = lyric
                            lyric_text = lyric_line
                    else:
                        if(len(lyric_text) + len(lyric_line) < 1024 ):
                            lyric_text = lyric_text + '\r\n' + lyric_line
                        else:
                            self.add_field(name='\u200B', value=lyric_text, inline=False)
                            lyric_text = lyric_line
                    self.add_field(name='\u200B', value=lyric_text, inline=False)
                    
        if self.lyrics_source:
            self.set_footer(text=self.lyrics_source)
        else:
            self.set_footer(text=EmptyEmbed)
