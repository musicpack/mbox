import asyncio
import discord
import logging
from typing import List
from src.music.element.MusicSource import MusicSource
from src.commander.element.ChatEmbed import ChatEmbed
from src.commander.element.Button import Button
from src.constants import *
class MusicQueue:
    """Reperesents a Queue GUI object. Handles which MusicSource to play next and displays in the GUI.
    """
    def __init__(self, active_embed: ChatEmbed, client: discord.Client, list: List[MusicSource] = []) -> None:
        self.list = list
        self.index = None
        self.client = client
        self.buttons = {
            'reset_all': Button(emoji='🗑️', client = self.client, action=self.reset_next_playing)
        }
        self.ChatEmbed = active_embed
        if not list:
            self.at_beginning = True
            self.at_end = False
        self.at_beginning = False
        self.at_end = False
    
    async def setup(self):
        self.ChatEmbed.actions = list(self.buttons.values())
        self.ChatEmbed.embed.title = 'Empty Queue'
        await self.ChatEmbed.update()

    def remove_index(self, index: int):
        """Removes a song from a list. Does not update ChatEmbed, call update_embed_from_queue() if needed."""
        return self.list.pop(index)
    
    async def reset_all(self):
        """Removes all MusicSources from the queue"""
        for music in self.list:
            music.cleanup()
        self.list = []
        self.index = None
        self.at_beginning = True
        self.at_end = False
        self.on_remove_all()
        await self.update_embed_from_queue()
    
    async def reset_next_playing(self):
        """Removes all but the current queued song from the list"""
        self.list = self.list[:self.index+1]
        await self.update_embed_from_queue()

    async def update_embed_from_queue(self) -> None:
        """Update the queue ChatEmbed based on state."""
        title = 'Queue Empty'
        if self.at_end or self.index == None or not self.list:
            self.ChatEmbed.embed.description = 'Your queue is empty. ' + USAGE_TEXT
            self.ChatEmbed.embed.title = title
            await self.ChatEmbed.update()
            return

        text_np = '**Now Playing**'
        text_n = '**Next**'
        description_np = ''
        description_n = ''
        
        for index in range(self.index, len(self.list)):
            if self.index == index:
                title = 'Queue'
                description_np += '\n> [' + self.list[index].info['title'] + '](' + self.list[index].info['webpage_url'] + ')'
            else:
                description_n += '\n> [' + self.list[index].info['title'] + '](' + self.list[index].info['webpage_url'] + ')'
        
        if description_np:
            self.ChatEmbed.embed.title = title

            description = text_np + description_np
            if description_n:
                description += '\n' + text_n + description_n

            self.ChatEmbed.embed.description = description
            await self.ChatEmbed.update()

    def add(self, music) -> None:
        """Add a MusicSource to the music queue. Updates the ChatEmbed."""
        self.list.append(music)
        asyncio.create_task(asyncio.coroutine(self.update_embed_from_queue)())

    
    def current(self):
        """Get the currently playing MusicSource"""
        if self.list:
            if self.index == None:
                return None
            else:
                return self.list[self.index]
        return None

    def next(self) -> MusicSource:
        """Get the next MusicSource and change the head to the next MusicSource. Updates the ChatEmbed."""
        if self.list:
            if self.at_beginning or self.index == None:
                self.index = 0
                self.at_beginning = False
                asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.update_embed_from_queue)(), self.client.loop)
                return self.list[self.index]
            elif self.index + 1 < len(self.list):
                self.at_end = False
                self.index += 1
                asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.update_embed_from_queue)(), self.client.loop)
                return self.list[self.index]
            else:
                self.at_end = True
                asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.update_embed_from_queue)(), self.client.loop)
                return None
        raise IndexError('MusicQueue list empty')

    def prev(self):
        """Get the previous MusicSource and changes the head to the previous MusicSource. Updates the ChatEmbed."""
        if self.list:
            if self.at_end:
                self.at_end = False
                asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.update_embed_from_queue)(), self.client.loop)
                return self.list[self.index]
            elif self.index - 1 >= 0:
                self.index -= 1
                asyncio.run_coroutine_threadsafe(asyncio.coroutine(self.update_embed_from_queue)(), self.client.loop)
                return self.list[self.index]
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