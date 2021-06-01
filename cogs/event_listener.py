from src.element.MusicBoxContext import MusicBoxContext
from typing import Union, List
import discord
from main import bot, logging
import src.preinitialization
from src.parser import parse
from src.command_handler import play_ytid
import src.element.profile
from discord_slash.utils.manage_commands import create_option
from discord.ext import commands
from src.constants import INVITE_LINK_FORMAT

COMMAND_CHANNEL_WARNING = 'Accepted command.'
watching_channels = []
profiles: List[src.element.profile.Profile] = []


class EventListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        logging.debug('Message from {0.author}: {0.content}'.format(message))

        # Ignore message if it was from a bot
        if message.author.bot:
            # Delete the message if its from another bot.
            # Any message created by the bot itself should be handled outside of this function.
            if message.author != self.bot.user:
                await message.delete()
            return

        # Top level command stop
        if message.content == 'stop':
            logging.info('Received stop from {0.name}'.format(message.author))
            await bot.logout()

        # Check which profile the message relates to
        for profile in profiles:
            if profile.guild == message.guild:

                # Check if the message comes from a command channel
                if profile.messenger.command_channel == message.channel:
                    await message.delete()

                    # Create a context
                    bot_ctx = MusicBoxContext(prefix='', profile=profile, name='', slash_context=None, message=message, args=[
                        message.content], kwargs={'command': message.content})

                    # Top level command test
                    if message.content == 'test':
                        logging.info(
                            'Received test from {0.name}'.format(message.author))
                        await profile.messenger.gui['player'].update()
                        break
                    # Top level command rem
                    if message.content == 'rem':
                        logging.info(
                            'Received rem from {0.name}'.format(message.author))
                        for action in profile.messenger.gui['player'].actions:
                            await action.remove_all()
                        break
                    # Top level command play
                    if message.content == 'play':
                        logging.info(
                            'Received play from {0.name}'.format(message.author))
                        await play_ytid('JwmGruvGt_I', bot_ctx)
                        break

                    await parse(bot_ctx)
                    break

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        logging.debug('Typing from {0.name}'.format(user))

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        logging.info(f'Joined Server: {guild.name}')
        try:
            await guild.text_channels[0].send('Thanks for adding Music Bot!')
            await src.preinitialization.generate_profile(guild, self.bot, profiles)
            for profile in profiles:
                await profile.setup()
        except discord.errors.Forbidden:
            owner_member: discord.Member = guild.owner
            if owner_member:
                content = f"You or a member in server {guild.name} added me without the right permissions. Try adding me again with the link: " + \
                    INVITE_LINK_FORMAT.format(self.bot.user.id)
                await owner_member.send(content=content)
            await guild.leave()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        logging.info('Removed from Server: {0.name}'.format(guild))
        for profile in profiles:
            if profile.guild == guild:
                await profile.messenger.unregister_all()
                profiles.remove(profile)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        if user != self.bot.user:
            if reaction.message.author == self.bot.user:
                await reaction.message.remove_reaction(reaction, user)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Makes sure the player stops playing the song if the bot was disconnected by force
        if member == self.bot.user:
            if before.channel and after.channel == None:
                for profile in profiles:
                    if profile.guild == member.guild:
                        profile.player.stop()

    @commands.Cog.listener()
    async def on_ready(self):
        await src.preinitialization.generate_profiles(bot.guilds, self.bot, profiles)
        for profile in profiles:
            await profile.setup()


def setup(bot):
    bot.add_cog(EventListener(bot))
