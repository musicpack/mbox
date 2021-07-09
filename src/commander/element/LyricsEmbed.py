from typing import List
from discord.embeds import Embed, EmptyEmbed
from src.constants import USAGE_TEXT
from mechanize import Browser
from bs4 import BeautifulSoup
from googlesearch import search


class LyricsEmbed(Embed):
    """Represents a Lyrics object. Subclass of a player object."""
    def __init__(self, **kwargs) -> None:
        # Call super first so that it doesn't overwrite custom variables in this class
        super().__init__(**kwargs)
        
        self.title = 'Lyrics'
        
        # Footer Variables
        self.lyrics: str = kwargs.get('lyrics', None)
        self.lyrics_source: str = kwargs.get('lyrics_source', None)

        self.song_title: str = kwargs.get('song_title', None)
        self.song_author: str = kwargs.get('song_author', None)

        if not self.lyrics and not self.lyrics_source and not self.song_title and not self.song_author:
            self.description = USAGE_TEXT
            return

        if not self.lyrics and not self.lyrics_source and self.song_title and self.song_author:
            self.lyrics = self.musixmatch_lyrics(self.song_title, self.song_author)
            self.lyrics_source = "From Musixmatch or Boom4u"

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

        splited_verses_list:List[str] = self.split_verse_if_over_limit(lyrics, max_description, max_embed_field)

        embed_field_verses = ''
        description_verses = ''

        for verse in splited_verses_list:
            if(embed_field_verses == ''):
                if(len(verse) + len(description_verses) < max_description):
                    description_verses = self.append_verse(description_verses, verse)
                else:
                    embed_field_verses = verse
            else:
                if(len(verse) + len(embed_field_verses) < max_embed_field):
                    embed_field_verses = self.append_verse(embed_field_verses, verse)
                else:
                    self.generate_embed_field(embed_field_verses)
                    embed_field_verses = verse
        self.generate_embed_field(embed_field_verses)
        return description_verses          


    def split_verse_if_over_limit(self, lyrics: str, max_description: int, max_embed_field: int) -> List[str]:
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
        verses:List[str] = self.get_verses(lyrics)

        if(len(verses[0]) < max_description):
            splited_verses_list.append(verses[0])
            del verses[0]

        else:
            splited_verses_list, verses[0] = self.split_verse(verses[0], splited_verses_list, max_description, max_embed_field, position=max_description)

        for verse in verses:
            if(len(verse) < max_embed_field):
                splited_verses_list.append(verse)

            else:
                splited_verses_list = self.split_verse(verse, splited_verses_list, max_description, max_embed_field, position=max_embed_field)

        return splited_verses_list


    def split_verse(self, verse:str, splited_verses_list:List[str], max_description:int , max_embed_field:int , position:int) -> str or List[str] :
        if(position == max_embed_field):
            
            while(len(verse) > position):
                move_left:int = self.find_starting_line_to_break(verse, position)
                splited_verses_list.append(verse[0:position - move_left])
                verse = verse[position - move_left:]
            splited_verses_list.append(verse)
            
            return splited_verses_list
        
        elif(position == max_description):
            move_left = self.find_starting_line_to_break(verse, position)
            splited_verses_list.append(verse[0:position - move_left])
            verse = verse[position - move_left:]

            return [splited_verses_list, verse]
        

    def find_starting_line_to_break(self, verse:str, position:int) -> int:
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


    def get_verses(self, lyrics: str) -> List[str]:
        return lyrics.split('\r\n\r\n')
    
    
    def append_verse(self, lyric: str, verse: str) -> str:
        return lyric + '\r\n\r\n' + verse


    def musixmatch_lyrics(self, song_name: str, song_artist: str) -> str:
        
        if(song_name == None and song_artist == None):
            return None

        site = None
        musixmatch_lyric = ''

        browser = Browser()
        self.enable_web_scrapper(browser)
            
        results = search('Musixmatch.com ' + song_name + ' ' + song_artist)

        for result in results:
            if(result[:27] == 'https://www.musixmatch.com/' and result[:33] != 'https://www.musixmatch.com/album/'):
                site = result
                break

        if site != None:
                
            browser.open(site)

            inspect_element = str(BeautifulSoup(browser.response().read(), "html.parser"))
            splitted_inspect_element = inspect_element.split('<span class="lyrics__content__ok">')

            if len(splitted_inspect_element) == 3:
                first_truncate = splitted_inspect_element[1].split('</span></p><div><div class="inline_video_ad_container_container">')
                second_truncate = splitted_inspect_element[2].split('</span></p></div></span><div></div><div><div class="lyrics-report" id="" style="position:relative;display:inline-block">')
                musixmatch_lyric = first_truncate[0] + '\r\n' + second_truncate[0]

            elif len(splitted_inspect_element) == 2:
                first_truncate = splitted_inspect_element[1].split('</span>')
                musixmatch_lyric = first_truncate[0]

            elif len(splitted_inspect_element) == 1:
                splitted_inspect_element = inspect_element.split('col-xs-6 col-sm-6 col-md-6 col-ml-6 col-lg-6')
                for line_index in range(3,len(splitted_inspect_element),2):
                    musixmatch_lyric = str(musixmatch_lyric) + "\r\n" + splitted_inspect_element[line_index][16:-24]
            return musixmatch_lyric
            
        return self.boom4u_lyrics(song_name, song_artist, browser)


    def boom4u_lyrics(self, song_name: str, song_artist: str, browser: Browser) -> str:

        site = None

        results = search('boom4u ' + song_name + ' ' + song_artist)
        for result in results:
            if(result[:22] == 'http://www.boom4u.net/'):
                site = result
        if site != None:
            browser.open(site)

            inspect_element = str(BeautifulSoup(browser.response().read(), "html.parser"))
            first_truncate = inspect_element.split('<table cellpadding="0" cellspacing="0" class="tabletext"><tr><td>')
            second_truncate = first_truncate[1].split('-----------------')
            third_truncate = second_truncate[0].split('<br/><tr><td>')

            del third_truncate[-3:-1]

            boom4u_lyric = '\r\n'.join(third_truncate)

            return boom4u_lyric
        return None


    def enable_web_scrapper(self, browser: Browser) -> None:
        browser.set_handle_robots(False)
        browser.addheaders = [('Referer', 'https://www.reddit.com'), ('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    
