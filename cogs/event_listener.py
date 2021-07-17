import logging
from typing import Union

import discord
from discord.ext import commands

from cogs.state_manager import StateManager
from src.command_handler import play_ytid
from src.element.database import Record
from src.element.MusicBoxContext import MusicBoxContext
from src.parser import parse


class EventListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.state: StateManager = self.bot.get_cog("StateManager")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        logging.debug(f"Message from {message.author}: {message.content}")

        # Ignore message if it was from a bot
        if message.author == self.bot.user:
            return

        # Ignore message if it came from a bot that was not from a webhook
        if message.author.bot and not message.webhook_id:
            return

        # TODO Check if its from a command channel
        # Check if the message comes from a command channel
        if self.state.config_db.is_command_channel(message.channel.id):
            await message.delete()

            # Top level command stop
            if message.content == "stop":
                logging.info(f"Received stop from {message.author.name}")
                await self.bot.logout()

            # Create a context
            bot_ctx = MusicBoxContext(
                prefix="",
                guild=message.guild,
                command_channel=message.channel.id,
                player=await self.state.get_player(message.guild.id),
                name="",
                slash_context=None,
                message=message,
                args=[message.content],
                kwargs={"command": message.content},
            )

            # Top level command play
            if message.content == "play":
                logging.info(f"Received play from {message.author.name}")
                await play_ytid("JwmGruvGt_I", bot_ctx)
                return

            await parse(bot_ctx)

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        logging.debug(f"Typing from {user.name}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):

        # Adding guild item to database first time bot joins server
        record = Record(guild_id=guild.id)
        put_response: dict = self.state.config_db.store_record(record)
        logging.info(f"Printing response from Dynamo: {put_response}")
        logging.info(f"Joined Server: {guild.name}")
        await guild.text_channels[0].send("Thanks for adding Music Bot!")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # TODO: Remove guild item from database
        logging.info(f"Removed from Server: {guild}")

    @commands.Cog.listener()
    async def on_reaction_add(
        self,
        reaction: discord.Reaction,
        user: Union[discord.Member, discord.User],
    ):
        if user != self.bot.user:
            if reaction.message.author == self.bot.user:
                await reaction.message.remove_reaction(reaction, user)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Makes sure the player stops playing the song if the bot was disconnected by force
        if member == self.bot.user:
            if before.channel and after.channel is None:
                player = await self.state.get_player(member.guild.id)
                player.stop()

    @commands.Cog.listener()
    async def on_ready(self):
        # TODO: Emulate preinitilizer functionality
        logging.info("Music Box is all set up and ready to go!")


def setup(bot):
    bot.add_cog(EventListener(bot))
