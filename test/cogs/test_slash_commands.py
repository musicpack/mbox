# from discord_slash.context import SlashContext
# from discord.ext.commands import Bot
# import pytest

# from cogs.slash_commands import SlashCommands
# from src.element.MusicBoxContext import MusicBoxContext

# @pytest.mark.asyncio
# async def test_process_slash_command():
#     class FakeSlashContext(SlashContext):
#         def __init__(self) -> None:
#             self.message = None  # Should be set later.
#             self.name = self.command = self.invoked_with = 'generic_command'
#             self.args = []
#             self.kwargs = {}
#             self.subcommand_name = self.invoked_subcommand = self.subcommand_passed = None
#             self.subcommand_group = self.invoked_subcommand_group = self.subcommand_group_passed = None
#             self.interaction_id = 'N/A'
#             self.command_id = 'N/A'
#             self._http = NotImplementedError
#             self.bot = NotImplementedError
#             self._logger = NotImplementedError
#             self.deferred = False
#             self.responded = False
#             self._deferred_hidden = False
#             self.guild_id = 0
#             self.author_id = 0
#             self.channel_id = 0
    
#     class FakeBot(Bot):
#         pass
    
#     def cb_function(mbox_ctx):
#         assert isinstance(mbox_ctx, MusicBoxContext)
#         assert mbox_ctx.prefix == '/'
#         assert isinstance(mbox_ctx.slash_context, FakeSlashContext)

#     a = SlashCommands(FakeBot)

#     await a.process_slash_command(FakeSlashContext, cb_function)