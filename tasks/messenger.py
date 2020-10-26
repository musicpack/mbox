from __future__ import annotations
import asyncio
from asyncio.tasks import Task
from types import FunctionType
import discord
from typing import List, Dict
import logging

class Messenger:
    def __init__(self, default_channel, client, command_channel: discord.TextChannel = None) -> None:
        self.default_channel: discord.TextChannel = default_channel
        self.command_channel: discord.TextChannel = command_channel
        self.client: discord.Client = client
        self.user = client.user
        self.gui: Dict[str, ChatEmbed] = {}
        self.set_gui()
    
    async def setup(self):
        await self.clean_chat()
        await self.send_gui()
    
    def set_gui(self) -> None:
        async def press():
            print('pressed')
        self.gui: Dict[str, ChatEmbed] = {
            'lyrics' : ChatEmbed('lyrics', {
                'title': 'Lyrics',
                'description': 'Play a song to display lyrics'
            }, self.command_channel, actions = [Button('🧰', self.client, action=press)])

        }
    
    def is_gui(self, message: discord.Message) -> bool:
        if len(message.embeds) == 1:
            for key in self.gui:
                if(self.gui[key].embed.title == message.embeds[0].title):
                    self.gui[key].message = message
                    return True
        return False
    
    async def unregister_all(self):
        chat_embed: ChatEmbed
        button: Button
        for chat_embed in self.gui.values():
            for button in chat_embed.actions:
                await button.remove_all(remove_reaction = False)

    async def clean_chat(self):
        await self.unregister_all()
        counter = 0
        deleted_messages: List[discord.Message]= []
        message: discord.Message
        async for message in self.command_channel.history(limit=101):
            counter += 1
            if counter > 100:
                self.command_channel.delete()

                music_box = await self.guild.create_text_channel(name='music-box')
                topic = 'Music Box controlled channel. Chat in this channel will be deleted. Version 0.1 ' + str(hash(music_box))
                await music_box.edit(topic=topic)

                self.command_channel = music_box
                return
            deleted_messages.append(message)
        
        print('deleted_messages: ' + str(len(deleted_messages)))
        await self.command_channel.delete_messages(deleted_messages)
                    
    
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

    async def register_buttons(self):
        for button in self.actions:
            await button.register(self.message)

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
                logging.error('Registering button ' + self.emoji + 'failed. Message already registered.')
        else:
            logging.error('Registering button ' + self.emoji + 'failed. You must provide a discord Message object.')
    
    async def remove(self, message: discord.Message):
        if self.coro[message]:
            await message.remove_reaction(self.emoji, self.client.user)
            self.coro[message].cancel()
            del self.coro[message]
        else:
            logging.error('Button remove failed, message does not exist')

    async def remove_all(self, remove_reaction = True):
        for key in list(self.coro):
            if remove_reaction:
                await key.remove_reaction(self.emoji, self.client.user)
            self.coro[key].cancel()
            del self.coro[key]
