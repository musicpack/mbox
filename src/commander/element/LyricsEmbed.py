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

        split_verse_list = self.split_verse(lyrics, max_description, max_embed_field)
        embed_verses = ''
        description_verses = ''
        count = 0
        for index in range(len(split_verse_list)):
            if(len(split_verse_list[index]) + len(description_verses) < max_description):
                description_verses = description_verses + '\r\n\r\n' + split_verse_list[index]
                count += 1
            else:
                break
        for index in range(count,len(split_verse_list)):
            if(len(split_verse_list[index]) + len(embed_verses) <= max_embed_field):
                embed_verses = embed_verses + '\r\n\r\n' + split_verse_list[index]
            else:
                self.add_field(name='\u200B', value=embed_verses, inline=False)
                embed_verses = split_verse_list[index]
        return description_verses          


    def split_verse(self, lyrics: str, max_description: int, max_embed_field: int) -> list[str]:
        return_verses = []
        verses = self.get_verses(lyrics)
        if(len(verses[0]) < max_description):
            return_verses.append(verses[0])
            del verses[0]
        else:
            count = self.find_end_line(verses[0], max_description)
            return_verses.append(verses[0][0:max_description - count])
            verses[0] = verses[max_description - count:]

        for index in range(len(verses)):
            if(len(verses[index]) < max_embed_field):
                return_verses.append(verses[index])
            else:
                while(len(verses[index]) > max_embed_field):
                    count = self.find_end_line(verses[index], max_embed_field)
                    return_verses.append(verses[index][0:max_embed_field - count])
                    verses[index] = verses[index][max_embed_field - count:]
                return_verses.append(verses[index])
        return return_verses

    def find_end_line(self, verse, position) -> int:
        count = 0
        while(verse[position - count] != '\r'):
            count += 1
        return count

    def get_verses(self, lyrics: str) -> list[str]:
        return lyrics.split('\r\n\r\n')
    
    def append_verse(self, lyric: str, verse: str) -> str:
        return lyric + '\r\n\r\n' + verse