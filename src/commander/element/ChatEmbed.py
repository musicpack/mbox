from __future__ import annotations
import discord
from typing import List
from src.commander.element.Button import Button

class ChatEmbed:
    """Base class for each GUI element (a message).

    Attributes:
        name (str): Name of the ChatEmbed
        embed_dict: discord.Embed() in a dictionary form
        text_channel: The command channel where this ChatEmbed sends messages to
        actions: A list of buttons for the ChatEmbed

    """
    def __init__(self, name, embed_dict, text_channel, actions: List[Button] = None) -> None:
        self.name = name
        self._dict = embed_dict
        self.embed: discord.Embed = discord.Embed().from_dict(embed_dict)
        self.text_channel : discord.TextChannel = text_channel
        self.message: discord.Message = None
        self.actions: List[Button] = actions
    
    def get_dict(self):
        print('got dict')
        return self._dict
    
    def set_dict(self, key, value):
        print('dict set')
        self._dict[key] = value

    async def send(self, register_buttons = True, content=None, *, tts=False, file=None, files=None, delete_after=None, nonce=None, allowed_mentions=None):
        """Sends this ChatEmbed to the text channel in this class.

        Args:
            register_buttons (bool, optional): Registers the button to this ChatEmbed. Defaults to True.
            content (string, optional): Message to preface the embed message. Defaults to None.
            tts (bool, optional): enable text to speech to the message (excludes embed message). Defaults to False.
            file (, optional): Defaults to None.
            files (, optional): Defaults to None.
            delete_after (, optional): time to automatically delete the message. Defaults to None.
            nonce (, optional): . Defaults to None.
            allowed_mentions (, optional): . Defaults to None.

        Returns:
            discord.Message: Message object sent
        """
        options = {
            'tts':tts,
            'embed':self.embed,
            'file':file,
            'files':files,
            'delete_after':delete_after,
            'nonce':nonce,
            'allowed_mentions':allowed_mentions
        }
        self.message = await self.text_channel.send(content, **options)
        if register_buttons:
            if self.actions:
                for button in self.actions:
                    await button.register(self.message)
        return self.message

    async def update(self, update_buttons = False):
        """Edit the current message with the class embed. Optionally can choose to update buttons as well."""
        if not self.message:
            raise Exception('Cannot update if GUI has not been sent yet.')
        await self.message.edit(suppress= False, embed=self.embed)
        # await self.remove_buttons()
        # await self.register_buttons()
        if update_buttons:
            if self.actions:
                for button in self.actions:
                    if not button.is_registered(self.message):
                        await button.register(self.message)
        return self.message

    async def remove_buttons(self):
        """Removes all the buttons registered to this ChatEmbed"""
        if self.actions:
            for button in self.actions:
                await button.remove_all()

    async def register_buttons(self):
        """Registered all the buttons registered to this ChatEmbed"""
        if self.actions:
            for button in self.actions:
                await button.register(self.message)