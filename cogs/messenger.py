from discord.client import Client
from discord.ext import commands, tasks

from cogs.state_manager import StateManager


class PanelManager(commands.Cog):
    def __init__(self, bot):
        self.bot: Client = bot
        self.state: StateManager = self.bot.get_cog("StateManager")
        self.panel_processor.start()

    def cog_unload(self):
        self.panel_processor.cancel()

    @tasks.loop(seconds=1.0)
    async def panel_processor(self):

        for key in list(self.state.panels):
            if self.state.panels[key].is_expired():
                await self.state.panels[key].delete()
                self.state.panels.pop(key)
            else:
                await self.state.panels[key].process()


def setup(bot):
    bot.add_cog(PanelManager(bot))
