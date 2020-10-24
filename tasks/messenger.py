from __future__ import annotations
import asyncio
from asyncio.tasks import Task
from types import FunctionType
import discord
from typing import List, Dict
import logging

class Messenger:
    def __init__(self, default_channel, client, command_channel = None) -> None:
        self.default_channel = default_channel
        self.command_channel = command_channel
        self.client = client
        self.user = client.user
        self.gui: Dict[str, ChatEmbed] = {}
        self.reset_gui()
    
    def reset_gui(self) -> None:
        async def press():
            print('pressed')
        self.gui: Dict[str, ChatEmbed] = {
            'lyrics' : ChatEmbed('lyrics', {
                'title': 'Lyrics',
                'description': 'Play a song to display lyrics'
            }, self.command_channel, actions = [Button('🧰', self.client, action=press)])

        }
    
    async def notify_action_required(self, err_msg, action_failed, action_sucesss, act_msg):
        text_channel = self.default_channel
        err_str = err_msg
        message_warning = await text_channel.send(err_str + '\n**Click on the toolbox below to auto finish setup!**')
        await message_warning.add_reaction('🧰')
        
        def check(reaction, user):
            return user != self.user and str(reaction.emoji) == '🧰'

        try:
            # Note: Using reaction_add event, which only gets exec when reactions are added to a message in bot cache
            reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await message_warning.edit(content=err_str+'\n~~Click on the toolbox below to auto finish setup!~~')
            await action_failed(text_channel)
        else:
            await message_warning.edit(content=err_str+'\n' + '**' + act_msg + '**')
            await action_sucesss(text_channel)

    async def send_gui(self):
        if self.command_channel:
            for chat_embed in self.gui.values():
                await chat_embed.send()

class ChatEmbed:
    def __init__(self, name, embed_dict, text_channel, actions: List[Button] = None) -> None:
        self.name = name
        self._dict = embed_dict
        self.embed = discord.Embed().from_dict(embed_dict)
        self.text_channel : discord.TextChannel = text_channel
        self.message = None
        self.actions: List[Button] = actions
    
    def get_dict(self):
        print('got dict')
        return self._dict
    
    def set_dict(self, key, value):
        print('dict set')
        self._dict[key] = value

    async def send(self, content=None, *, tts=False, file=None, files=None, delete_after=None, nonce=None, allowed_mentions=None):
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
        for button in self.actions:
            await button.register(self.message)
        return self.message

class Button:
    def __init__(self, emoji, client: discord.Client, *, timeout = None, action: FunctionType = None, action_timeout: FunctionType = None):
        self.emoji = emoji
        self.client = client
        self.timeout = timeout
        self.action = action
        self.action_timeout = action_timeout
        self.coro: Dict[discord.Message, Task] = {}
    
    # TODO Function needs testing to make sure it doesn't spawn unnessasary threads
    async def register(self, message: discord.Message):
        if type(message) == discord.Message:
            if message not in self.coro:
                await message.add_reaction(self.emoji)

                async def refresh():
                    def check(reaction, user):
                        return user != self.client.user and str(reaction.emoji) == self.emoji and reaction.message.id == message.id
                    
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=self.timeout, check=check)
                    except asyncio.TimeoutError:
                        await message.remove_reaction(self.emoji, self.client.user)
                        logging.info(self.emoji + ' reaction button timed out')
                        await self.action_timeout()
                    except asyncio.CancelledError:
                        logging.debug(self.emoji + ' canceled')
                        raise
                    else:
                        logging.debug(self.emoji + ' pressed')
                        await self.action()
                
                self.coro[message] = asyncio.create_task(asyncio.coroutine(refresh)())
                while self.coro[message]:
                    await self.coro[message]
                    self.coro[message] = asyncio.create_task(asyncio.coroutine(refresh)())
            else:
                logging.error('Registering button ' + self.emoji + 'failed. Message already exists.')
        else:
            logging.error('Registering button ' + self.emoji + 'failed. You must provide a discord Message object.')
    
    async def remove_all(self):
        for key in list(self.coro):
            await key.remove_reaction(self.emoji, self.client.user)
            await key.delete()
            self.coro[key].cancel()
            del self.coro[key]
            print(len(self.coro))
