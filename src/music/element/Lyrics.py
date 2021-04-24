from typing import List
from src.commander.element.Button import Button
from src.commander.element.ChatEmbed import ChatEmbed
from src.constants import *
import discord
import logging
from ytmusicapi import YTMusic

"""NOTE: This is a model class. Any class that represents just a GUI object should emulate this file."""

class Lyrics(ChatEmbed):
    """Represents a Lyrics object. Subclass of a player object."""
    def __init__(self, text_channel: discord.TextChannel) -> None:
        embed = {
                'title': 'Lyrics',
                'description': USAGE_TEXT
                }
        super().__init__(name='lyrics',embed_dict= embed, text_channel=text_channel, actions=[])

        self.lyrics = None
        self.source = None

    def setup(self):
        """Lyrics object does not need a setup. This function is depricated."""
        logging.warn('Depricated: lyrics setup function called.')
        pass

    def get_lyrics(self, youtube_id: str) -> bool:
        """Gets lyrics (if exists) given the youtube id.
        Returns True if successful, False if no lyrics
        NOTE: get_lyrics operation is wasteful as it discards a watch playlist while getting lyrics."""
        ytmusic = YTMusic()
        # TODO: Make more efficent use of watch_playlist
        watch_playlist = ytmusic.get_watch_playlist(videoId=youtube_id)

        browse_id = watch_playlist['lyrics']
        if browse_id:
            result = ytmusic.get_lyrics(browse_id)
            self.lyrics = result['lyrics']
            self.source = result['source']
            return True

        self.lyrics = None
        self.source = None
        return False

    async def send_lyrics(self, lyrics= None, source = None):
        """Sends the GUI lyrics. If arguments are provided, it will update those as well.

        Args:
            lyrics (str, optional): Send and update the lyrics. Defaults to None.
            source (str, optional): Send and update the source. Defaults to None.
        """
        if lyrics: self.lyrics = lyrics
        if source: self.source = source

        if self.lyrics:
            self.embed.description = self.lyrics[:2048] # TODO Support lyrics that are longer then the embed text limit in discord. (Page pagination?)
            if len(self.lyrics) > 2048:
                self.source += ' [Discord message limit reached. Lyrics truncated.]'
        else:
            self.embed.description = 'No lyrics found for this song.'

        if self.source:
            self.embed.set_footer(text=self.source)
        else:
            self.embed.set_footer(text='')
        await self.update()
    
    async def update_lyrics(self, youtube_id) -> bool:
        """Gets lyrics and updates the embed to represent that state.
        Args:
            youtube_id: str Youtube Id of the lyrics that you want to update.
        Returns bool
            True if there was lyrics to the song.
            False if there was no lyrics for the current song."""
        lyrics_found_state = self.get_lyrics(youtube_id)
        await self.send_lyrics()

        return lyrics_found_state
            
        

    async def reset(self):
        """Removes all lyrics and resets to uninitiated state."""
        self.lyrics = USAGE_TEXT
        self.source = None

        self.embed.description = self.lyrics
        self.embed.set_footer(text='')

        await self.update()

    
