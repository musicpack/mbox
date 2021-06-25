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
            self.description = self.get_description(self.lyrics, self.max_description, self.max_embed_field)

                             
        if self.lyrics_source:
            self.set_footer(text=self.lyrics_source)
        else:
            self.set_footer(text=EmptyEmbed)
        
    
    def get_description(self, lyrics: str, max_description: int, max_embed_field: int) -> str:
        if(len(lyrics) < max_description):
            return lyrics

        splited_verses_list:list[str] = self.split_verse_if_over_limit(lyrics, max_description, max_embed_field)

        embed_field_verses = ''
        description_verses = ''

        index_value = 0
        for index in range(len(splited_verses_list)):
            if(len(splited_verses_list[index]) + len(description_verses) < max_description):
                description_verses = description_verses + '\r\n\r\n' + splited_verses_list[index]
                index_value += 1
            else:
                break

        for index in range(index_value,len(splited_verses_list)):
            if(len(splited_verses_list[index]) + len(embed_field_verses) <= max_embed_field):
                embed_field_verses = embed_field_verses + '\r\n\r\n' + splited_verses_list[index]
            else:
                self.generate_embed_field(embed_field_verses)
                embed_field_verses = splited_verses_list[index]

        return description_verses          


    def split_verse_if_over_limit(self, lyrics: str, max_description: int, max_embed_field: int) -> list[str]:
        """
        return the splitted verses where we split verses if...
            if characters inside description is over 2048 and
            if characters inside embed field is over 1024.
        
        parameters
            lyrics: str           =>  music lyric
            max_description: int  =>  2048
            max_embed_field: int  =>  1024
        """
        
        splited_verses_list = []
        verses:list[str] = self.get_verses(lyrics)

        if(len(verses[0]) < max_description):
            splited_verses_list.append(verses[0])
            del verses[0]

        else:
            move_left = self.find_starting_line_to_break(verses[0], max_description)
            splited_verses_list.append(verses[0][0:max_description - move_left])
            verses[0] = verses[max_description - move_left:]

        for index in range(len(verses)):
            if(len(verses[index]) < max_embed_field):
                splited_verses_list.append(verses[index])

            else:
                while(len(verses[index]) > max_embed_field):
                    move_left:int = self.find_starting_line_to_break(verses[index], max_embed_field)
                    splited_verses_list.append(verses[index][0:max_embed_field - move_left])
                    verses[index] = verses[index][max_embed_field - move_left:]
                splited_verses_list.append(verses[index])

        return splited_verses_list

    def find_starting_line_to_break(self, verse, position) -> int:
        '''
        return the value where we cut off between the line

        ex) I will destory this world and nobody will survive
            But I will be the one who will live in this world

        breaks into 

            I will destory this world and nobody will survive
            But I will be the one wh
            
            o will live in this world
        
        count length btw "But I will be the one wh" to break the line which looks like...

            I will destory this world and nobody will survive
            
            But I will be the one who will live in this world

        Parameter:
            verse: str      =>  verse inside the song
            position: int   =>  position to cut off verse (1024 or 2048)

        '''
        move_left = 0
        while(verse[position - move_left] != '\n'):
            move_left += 1
        return move_left

    def generate_embed_field(self, embed_field_verses: str) -> None:
        '''
        create the embed_textfield under description
        '''
        self.add_field(name='\u200B', value=embed_field_verses, inline=False)

    def get_verses(self, lyrics: str) -> list[str]:
        return lyrics.split('\r\n\r\n')
    
    def append_verse(self, lyric: str, verse: str) -> str:
        return lyric + '\r\n\r\n' + verse