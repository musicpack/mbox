import logging
import discord
from src.commander.element.Button import Button
from src.commander.element.ChatEmbed import ChatEmbed
from src.constants import VERSION


class Reporter(ChatEmbed):
    def __init__(self, client, text_channel: discord.TextChannel) -> None:
        embed = {
                'title': 'Music Box ' + VERSION,
                'description': "\n**Please mute this channel to avoid notification spam!**" +
                "\n**NEW!!** Try slash commands `/play`" +
                "\n*Early Access, please report any bugs!*" +
                "\n[Help](https://github.com/borisliao/mbox/wiki/Help) | [Changelog](https://github.com/borisliao/mbox/blob/master/CHANGELOG.md) | [About](https://github.com/borisliao/mbox)\n"
                }
        
        self.client = client

        super().__init__(name='Reporter',embed_dict= embed, text_channel= text_channel, actions=[])
        self.buttons = {
            # 'refresh': Button(emoji='🔄', client = self.client, action=self.refresh),
            # 'logout': Button(emoji='🟥', client = self.client, action=self.logout)
        }
        
    
    async def setup(self):
         """Reporter object does not need a setup. This function is depricated."""
         logging.warn('Depricated: lyrics setup function called.')
         pass


