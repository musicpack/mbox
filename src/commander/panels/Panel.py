import logging
from abc import ABC, abstractmethod
from time import time

from discord import TextChannel
from discord.ext import tasks


class Panel(ABC):
    expires = time() + 60  # Panel expires 60 seconds after creation
    refresh_rate = 14  # seconds
    id = None

    def __init__(self, text_channel: TextChannel):
        self.text_channel = text_channel

    @abstractmethod
    async def send(self):
        """Sends/edits the panel to the text channel."""
        pass

    @abstractmethod
    async def update(self):
        """Updates the panel to have new information based on state."""
        pass

    @abstractmethod
    async def delete(self):
        """Deletes the panel from the text channel."""
        pass

    async def process(self):
        """Handles reading the state and sending it to discord.

        This higher level function combines the .send and .update methods.
        In the CRUD Lifecycle this method does the reading and updating of the Panel.
        """
        if self.refresh_time > time():
            return
        else:
            self.refresh_time = time() + self.refresh_rate

        await self.update()
        await self.send()

    @tasks.loop(seconds=refresh_rate)
    async def task(self):
        if self.expires and self.expires < time():
            logging.info(
                f"Panel {self.text_channel.guild.id}:{self.id} expired."
            )
            self.delete_panel(self.text_channel.guild.id, panel_id=self.id)
            self.task.stop()

        if self.refresh_rate != self.task.seconds:
            self.task.change_interval(seconds=self.refresh_rate)
            self.task.restart()
            return

        await self.process()

    def delete_panel(self, guild_id: int, panel_id: str):
        pass
