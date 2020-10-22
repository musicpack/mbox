import asyncio
import discord
from typing import Dict
# from __future__ import annotations

class Messenger:
    def __init__(self, default_channel, client, command_channel = None) -> None:
        self.default_channel = default_channel
        self.command_channel = command_channel
        self.client = client
        self.user = client.user
        self.gui: Dict[str, ChatEmbed] = {}
        self.reset_gui()
    
    def reset_gui(self) -> None:
        self.gui: Dict[str, ChatEmbed] = {
            'lyrics' : ChatEmbed('lyrics', {
                'title': 'Lyrics',
                'description': 'Play a song to display lyrics'
            }, self.command_channel)

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
    def __init__(self, name, embed_dict, text_channel) -> None:
        self.name = name
        self._dict = embed_dict
        self.embed = discord.Embed().from_dict(embed_dict)
        self.text_channel : discord.TextChannel = text_channel
        self.message = None
    
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
        return self.message