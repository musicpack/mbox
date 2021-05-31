from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from requests.models import guess_filename
import src.preinitialization
import src.parser
import src.element.profile
from src.constants import *
from config import GUILD_ID
from src.element.context import Context
import discord
from cogs.event_listener import profiles

COMMAND_CHANNEL_WARNING = 'Accepted command.'


class MusicController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="test",
                       guild_ids=[GUILD_ID],
                       )
    async def _test(self, ctx: SlashContext):
        embed = discord.Embed(title="embed test")
        await ctx.send(content="test", embeds=[embed])

    async def process_slash_command(self, ctx: SlashContext, f):
        for profile in profiles:
            if profile.guild == ctx.guild:
                mbox_ctx = Context(prefix='/', profile=profile, name=ctx.name,
                                   slash_context=ctx, message=ctx.message, args=ctx.args, kwargs=ctx.kwargs)
                if ctx.channel == profile.messenger.command_channel:
                    await ctx.send(content=COMMAND_CHANNEL_WARNING)
                    await f(mbox_ctx)
                    await ctx.message.delete()
                    return
                else:
                    await ctx.defer(hidden=True)
                    status = await f(mbox_ctx)
                break

        await ctx.send(content=f"{status}", hidden=True)

    @cog_ext.cog_slash(name="youtube",
                       guild_ids=[GUILD_ID],
                       description='Add a youtube video to the queue.',
                       options=[
                           create_option(
                               name="search",
                               description="Name or link of a youtube video",
                               option_type=3,
                               required=True
                           )
                       ])
    async def _youtube(self, ctx: SlashContext, search):
        await self.process_slash_command(ctx, src.parser.message)

    @cog_ext.cog_slash(name="prev",
                       guild_ids=[GUILD_ID],
                       description='Goes to the previous song.')
    async def _prev(self, ctx: SlashContext):
        await self.process_slash_command(ctx, src.parser.player_prev)

    @cog_ext.cog_slash(name="next",
                       guild_ids=[GUILD_ID],
                       description='Goes to the next song.')
    async def _next(self, ctx: SlashContext):
        await self.process_slash_command(ctx, src.parser.player_next)

    @cog_ext.cog_slash(name="play",
                       description='Plays or resumes a song.',
                       guild_ids=[GUILD_ID],
                       options=[
                           create_option(
                               name="song_name_or_link",
                               description="Adds this song to the queue.",
                               option_type=3,
                               required=False
                           )
                       ])
    async def _play(self, ctx: SlashContext, song_name_or_link=None):
        print("yes")
        if song_name_or_link:
            await self.process_slash_command(ctx, src.parser.message)
        else:
            await self.process_slash_command(ctx, src.parser.resume_player)

    @cog_ext.cog_slash(name="pause",
                       description='Pauses actively playing song',
                       guild_ids=[GUILD_ID],
                       )
    async def _pause(self, ctx: SlashContext):
        await self.process_slash_command(ctx, src.parser.pause_player)


def setup(bot):
    bot.add_cog(MusicController(bot))