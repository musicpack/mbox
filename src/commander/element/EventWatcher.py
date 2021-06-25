import discord
import asyncio
import logging
import inspect
from types import FunctionType
from typing import Dict
from discord import emoji
from discord_components import Interaction

class EventWatcher:
    """
    Handles on press events and actions.
    """
    def __init__(self, client: discord.Client):
        self.client = client
        self.coro: Dict[str, asyncio.Task] = {}
    
    async def watch_button_click(self, emoji: str, timeout = None, action: FunctionType = None, action_timeout: FunctionType = None):
        if emoji not in self.coro:

            async def refresh():
                def check(interaction: Interaction):
                    return interaction.component.emoji.name == emoji

                try:
                    interaction: Interaction = await self.client.wait_for('button_click', timeout=timeout, check=check)
                except asyncio.TimeoutError:
                    logging.info(emoji + ' button_click event timed out')
                    await self.exec_and_await(action_timeout)
                else:
                    logging.debug(emoji + ' button_click event pressed')
                    self.coro[emoji] = asyncio.create_task(refresh())
                    await self.exec_and_await(action)
                    await interaction.respond(type=6)
        
            self.coro[emoji] = asyncio.create_task(refresh())

        else:
            logging.error(f'button_click: {emoji} event is already registered.')
    
    async def exec_and_await(self, function):
        res = function()
        if inspect.isawaitable(res):
            await res
    
    async def remove(self, emoji: str):
        """Removes this event from the eventwatcher.
        
        This function cancels the coroutine."""
        if self.coro[emoji]:
            self.coro[emoji].cancel()
            del self.coro[emoji]
        else:
            logging.error('Label does not exist.')

    async def remove_all(self):
        """Removes all events from the eventwatcher.
        
        This function cancels the coroutine."""
        for key in list(self.coro):
            self.coro[key].cancel()
            del self.coro[key]
