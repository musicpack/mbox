from typing import List
from discord.embeds import Embed, EmptyEmbed
from src.constants import USAGE_TEXT


class LyricsEmbed(Embed):
    """Represents a Lyrics object. Subclass of a player object."""

    def __init__(self, **kwargs) -> None:
        # Call super first so that it doesn't overwrite custom variables in this class
        super().__init__(**kwargs)

        self.title = "Lyrics"

        # Footer Variables
        self.lyrics: str = kwargs.get("lyrics", None)
        self.lyrics_source: str = kwargs.get("lyrics_source", None)

        if not self.lyrics and not self.lyrics_source:
            self.description = USAGE_TEXT
            return

        if self.lyrics:
            self.max_description = 2048
            self.max_embed_field = 1024
            self.description = self.get_description(
                self.lyrics, self.max_description, self.max_embed_field
            )

        if self.lyrics_source:
            self.set_footer(text=self.lyrics_source)
        else:
            self.set_footer(text=EmptyEmbed)

    def get_description(
        self, lyrics: str, max_description: int, max_embed_field: int
    ) -> str:
        if len(lyrics) < max_description:
            return lyrics

        splited_verses_list: List[str] = self.split_verse_if_over_limit(
            lyrics, max_description, max_embed_field
        )

        embed_field_verses = ""
        description_verses = ""

        for verse in splited_verses_list:
            if embed_field_verses == "":
                if len(verse) + len(description_verses) < max_description:
                    description_verses = self.append_verse(
                        description_verses, verse
                    )
                else:
                    embed_field_verses = verse
            else:
                if len(verse) + len(embed_field_verses) < max_embed_field:
                    embed_field_verses = self.append_verse(
                        embed_field_verses, verse
                    )
                else:
                    self.generate_embed_field(embed_field_verses)
                    embed_field_verses = verse
        self.generate_embed_field(embed_field_verses)
        return description_verses

    def split_verse_if_over_limit(
        self, lyrics: str, max_description: int, max_embed_field: int
    ) -> List[str]:
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
        verses: List[str] = self.get_verses(lyrics)

        if len(verses[0]) < max_description:
            splited_verses_list.append(verses[0])
            del verses[0]

        else:
            splited_verses_list, verses[0] = self.split_verse(
                verses[0],
                splited_verses_list,
                max_description,
                max_embed_field,
                position=max_description,
            )

        for verse in verses:
            if len(verse) < max_embed_field:
                splited_verses_list.append(verse)

            else:
                splited_verses_list = self.split_verse(
                    verse,
                    splited_verses_list,
                    max_description,
                    max_embed_field,
                    position=max_embed_field,
                )

        return splited_verses_list

    def split_verse(
        self,
        verse: str,
        splited_verses_list: List[str],
        max_description: int,
        max_embed_field: int,
        position: int,
    ) -> str or List[str]:
        if position == max_embed_field:

            while len(verse) > position:
                move_left: int = self.find_starting_line_to_break(
                    verse, position
                )
                splited_verses_list.append(verse[0 : position - move_left])
                verse = verse[position - move_left :]
            splited_verses_list.append(verse)

            return splited_verses_list

        elif position == max_description:
            move_left = self.find_starting_line_to_break(verse, position)
            splited_verses_list.append(verse[0 : position - move_left])
            verse = verse[position - move_left :]

            return [splited_verses_list, verse]

    def find_starting_line_to_break(self, verse: str, position: int) -> int:
        """
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

        """
        move_left = 0
        while verse[position - move_left] != "\n":
            move_left += 1
        return move_left

    def generate_embed_field(self, embed_field_verses: str) -> None:
        """
        create the embed_textfield under description
        """
        self.add_field(name="\u200B", value=embed_field_verses, inline=False)

    def get_verses(self, lyrics: str) -> List[str]:
        return lyrics.split("\r\n\r\n")

    def append_verse(self, lyric: str, verse: str) -> str:
        return lyric + "\r\n\r\n" + verse
