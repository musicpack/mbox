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
            self.max_textfield = 1024
            self.get_lyric() # self.description = self.get_lyric() 
                             
        if self.lyrics_source:
            self.set_footer(text=self.lyrics_source)
        else:
            self.set_footer(text=EmptyEmbed)
        
    
    def get_lyric(self):
        self.description_lyric = ''
        self.embed_field_lyric = ''

        lyric_list_by_gap = self.get_split_lyric_by_gap()
        lyric_list_by_line = self.get_split_lyric_by_line()
        split_type = self.get_split_type(lyric_list_by_gap)
        
        if(self.has_gap(lyric_list_by_gap) == True):
            self.split_lyric(lyric_list_by_gap, split_type)
        else:
            self.split_lyric(lyric_list_by_line, split_type)
            

    def split_lyric(self, lyric_list, split_type):
        for lyric_line in lyric_list:
            if(self.embed_field_lyric == ''):
                self.add_description_text(lyric_list, lyric_line, split_type)
            else:
                self.add_embed_field_text(lyric_list, lyric_line, split_type)
        self.add_field(name='\u200B', value=self.embed_field_lyric, inline=False)
        self.description = self.description_lyric


    def add_description_text(self, lyric_list, lyric_line, split_type):
        if(len(self.description_lyric) + len(lyric_line) < self.max_description ):
            self.description_lyric = self.description_lyric + split_type + lyric_line
        else:
            self.description = self.description_lyric
            self.embed_field_lyric = lyric_line


    def add_embed_field_text(self, lyric_list, lyric_line, split_type):
        if(len(self.embed_field_lyric) + len(lyric_line) < self.max_textfield ):
            self.embed_field_lyric = self.embed_field_lyric + split_type + lyric_line
                
        else:
            self.add_field(name='\u200B', value=self.embed_field_lyric, inline=False)
            self.embed_field_lyric = lyric_line


    def get_split_type(self, lyric_list: list) -> str:
        if(len(lyric_list) > 1):
            return '\r\n\r\n'
        elif(len(lyric_list) == 1):
            return '\r\n'
        

    def has_gap(self, lyric_list: list) -> bool:
        if(len(lyric_list) > 1):
            return True
        elif(len(lyric_list) == 1):
            return False


    def get_split_lyric_by_gap(self) -> list:
        return self.lyrics.split('\r\n\r\n')


    def get_split_lyric_by_line(self) -> list:
        return self.lyrics[0].split('\r\n')