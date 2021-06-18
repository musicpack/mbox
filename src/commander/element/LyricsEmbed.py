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
            self.lyric_display()
                             
        if self.lyrics_source:
            self.set_footer(text=self.lyrics_source)
        else:
            self.set_footer(text=EmptyEmbed)
        
    
    def lyric_display(self):
        self.lyric = ''
        self.embed_field = ''
        self.gap = ''
        lyric_list = self.lyrics.split('\r\n\r\n')

        #Lyric with gaps
        if(len(lyric_list) > 1):
            self.gap = '\r\n\r\n'
            self.separate_gap(lyric_list)

        #Lyric without gap
        elif(len(lyric_list) == 1):
            self.gap = '\r\n'
            self.separate_line(lyric_list)
            

    def separate_gap(self, lyric_list):
        for lyric_line in lyric_list:
            if(self.embed_field == ''):
                self.attach_description(lyric_list, lyric_line)
            else:
                self.attach_textfield(lyric_list, lyric_line)
    

    def separate_line(self, lyric_list):
        new_lyric_list = lyric_list[0].split('\r\n')
        for lyric_line in new_lyric_list:
            if(self.embed_field == ''):
                self.attach_description(new_lyric_list, lyric_line)
            elif (self.embed_field != ''):
                self.attach_textfield(new_lyric_list, lyric_line)


    def attach_description(self, lyric_list, lyric_line):
        if(len(self.lyric) + len(lyric_line) < self.max_description ):
            self.lyric = self.lyric + self.gap + lyric_line
            if(lyric_list[-1] == lyric_line):
                self.description = self.lyric
        else:
            self.description = self.lyric
            self.embed_field = lyric_line


    def attach_textfield(self, lyric_list, lyric_line):
        if(len(self.embed_field) + len(lyric_line) < self.max_textfield ):
            self.embed_field = self.embed_field + self.gap + lyric_line
            if(lyric_list[-1] == lyric_line):
                self.add_field(name='\u200B', value=self.embed_field, inline=False)
        else:
            self.add_field(name='\u200B', value=self.embed_field, inline=False)
            self.embed_field = lyric_line