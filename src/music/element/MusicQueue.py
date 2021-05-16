import asyncio
import discord
import logging
from typing import List
from src.music.element.MusicSource import MusicSource
from src.commander.element.ChatEmbed import ChatEmbed
from src.commander.element.Button import Button
from src.constants import *
class MusicQueue (ChatEmbed):
    """Reperesents a Queue GUI object. Handles which MusicSource to play next and displays in the GUI.
    """
    def __init__(self, client: discord.Client, text_channel: discord.TextChannel, playlist: List[MusicSource] = None) -> None:
        embed = {
                'title': 'Queue',
                'description': 'Nothing is in your queue. ' + USAGE_TEXT
                }
        super().__init__(name='MusicQueue',embed_dict= embed, text_channel= text_channel, actions=[])

        if playlist:
            self.playlist = playlist
        else:
            self.playlist = []
        self.index = None
        self.client = client
        self.buttons = {
            'reset_all': Button(emoji='🗑️', client = self.client, action=self.reset_next_playing)
        }
        if not list:
            self.at_beginning = True
            self.at_end = False
        self.at_beginning = False
        self.at_end = False
    
    """ Initial setup for the MusicQueue object """
    async def setup(self):
        self.actions = list(self.buttons.values())
        self.embed.title = 'Empty Queue'
        await self.update()

    def remove_index(self, index: int):
        """Removes a song from a list. Does not update ChatEmbed, call update_embed_from_queue() if needed."""
        return self.playlist.pop(index)
    
    async def reset_all(self):
        """Removes all MusicSources from the queue"""
        for music in self.playlist:
            music.cleanup() # TODO: Handle if the cleanup failes in error because the code below it will not run
        self.playlist = []
        self.index = None
        self.at_beginning = True
        self.at_end = False
        self.on_remove_all()
        await self.update_embed_from_queue()
    
    async def reset_next_playing(self):
        """Removes all but the current queued song from the list"""
        self.playlist = self.playlist[:self.index+1]
        await self.update_embed_from_queue()

    async def update_embed_from_queue(self) -> None:
        """Update the queue ChatEmbed based on state."""
        title = 'Queue Empty'
        if self.at_end or self.index == None or not self.playlist:
            self.embed.description = 'Your queue is empty. ' + USAGE_TEXT
            self.embed.title = title
            await self.update()
            return

        text_np = '**Now Playing**'
        text_n = '**Next**'
        description_np = ''
        description_n = ''
        
        for index in range(self.index, len(self.playlist)):
            if self.index == index:
                title = 'Queue'
                description_np += '\n> [' + self.playlist[index].info['title'] + '](' + self.playlist[index].info['webpage_url'] + ')'
            else:
                description_n += '\n> [' + self.playlist[index].info['title'] + '](' + self.playlist[index].info['webpage_url'] + ')'
        
        if description_np:
            self.embed.title = title

            description = text_np + description_np
            if description_n:
                description += '\n' + text_n + description_n

            self.embed.description = description
            await self.update()

    def add(self, music) -> None:
        """Add a MusicSource to the music queue. Updates the ChatEmbed."""
        self.playlist.append(music)
        asyncio.create_task(self.update_embed_from_queue())

    
    def current(self):
        """Get the currently playing MusicSource"""
        if self.playlist:
            if self.index == None:
                return None
            else:
                return self.playlist[self.index]
        return None

    def next(self) -> MusicSource:
        """Get the next MusicSource and change the head to the next MusicSource. Updates the ChatEmbed."""
        if self.playlist:
            if self.at_beginning or self.index == None:
                self.index = 0
                self.at_beginning = False
                asyncio.run_coroutine_threadsafe(self.update_embed_from_queue(), self.client.loop)
                return self.playlist[self.index]
            elif self.index + 1 < len(self.playlist):
                self.at_end = False
                self.index += 1
                asyncio.run_coroutine_threadsafe(self.update_embed_from_queue(), self.client.loop)
                return self.playlist[self.index]
            else:
                self.at_end = True
                asyncio.run_coroutine_threadsafe(self.update_embed_from_queue(), self.client.loop)
                return None
        raise IndexError('MusicQueue list empty')

    def prev(self):
        """Get the previous MusicSource and changes the head to the previous MusicSource. Updates the ChatEmbed."""
        if self.playlist:
            if self.at_end:
                self.at_end = False
                asyncio.run_coroutine_threadsafe(self.update_embed_from_queue(), self.client.loop)
                return self.playlist[self.index]
            elif self.index - 1 >= 0:
                self.index -= 1
                asyncio.run_coroutine_threadsafe(self.update_embed_from_queue(), self.client.loop)
                return self.playlist[self.index]
            else:
                return None
        raise IndexError('MusicQueue list empty')

    def event(self, event):
        """A decorator that registers an event to listen to.

          Events
        ---------
        on_remove_all()
        """

        setattr(self, event.__name__, event)
        logging.debug('%s has successfully been registered as an event', event.__name__)
        return event
    
    def on_remove_all(self):
        """Event function called when reset_all is called. Placeholder function to be overwritten."""
        pass
