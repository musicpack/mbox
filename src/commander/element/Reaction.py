import discord
import asyncio
import logging
import inspect
from types import FunctionType
from typing import Dict


class Reaction:
    """Base class for each reaction on a message.

    Handles on press events and actions for a button press.
    """

    def __init__(
        self,
        emoji,
        client: discord.Client,
        *,
        timeout=None,
        action: FunctionType = None,
        action_timeout: FunctionType = None
    ):
        self.emoji = emoji
        self.client = client
        self.timeout = timeout
        self.action = action
        self.action_timeout = action_timeout
        self.coro: Dict[discord.Message, asyncio.Task] = {}

    def is_registered(self, message: discord.Message):
        """Check if a message had this button assigned to it.

        Buttons assigned to this message are watching for a button press event."""
        if message in self.coro:
            return True
        return False

    # TODO Function needs testing to make sure it doesn't spawn unnessasary tasks
    async def register(self, message: discord.Message):
        """Registers this button to the message.

        Registering adds a reaction to the message and adds a coroutine to watch for button presses.
        """
        if type(message) == discord.Message:
            if message not in self.coro:
                await message.add_reaction(self.emoji)

                async def refresh():
                    def check(reaction, user):
                        return (
                            user != self.client.user
                            and str(reaction.emoji) == self.emoji
                            and reaction.message.id == message.id
                        )

                    try:
                        reaction, user = await self.client.wait_for(
                            "reaction_add", timeout=self.timeout, check=check
                        )
                    except asyncio.TimeoutError:
                        await message.remove_reaction(
                            self.emoji, self.client.user
                        )
                        logging.info(self.emoji + " reaction button timed out")
                        res = self.action_timeout()
                        if inspect.isawaitable(res):
                            await res
                    except asyncio.CancelledError:
                        logging.debug(self.emoji + " canceled")
                        raise
                    else:
                        logging.debug(self.emoji + " pressed")
                        self.coro[message] = asyncio.create_task(refresh())
                        res = self.action()
                        if inspect.isawaitable(res):
                            await res

                self.coro[message] = asyncio.create_task(refresh())
            else:
                logging.error(
                    "Registering button "
                    + self.emoji
                    + "failed. Message already registered."
                )
        else:
            logging.error(
                "Registering button "
                + self.emoji
                + "failed. You must provide a discord Message object."
            )

    async def remove(self, message: discord.Message):
        """Removes this button from a message. This function also cancels the coroutine to watch for new button presses."""
        if self.coro[message]:
            await message.remove_reaction(self.emoji, self.client.user)
            self.coro[message].cancel()
            del self.coro[message]
        else:
            logging.error(
                "Button remove failed, button does not exist in that Message"
            )

    async def remove_all(self, remove_reaction=True):
        """Removes this button from all messages. This function also cancels the coroutines to watch for new button presses from all messages."""
        for key in list(self.coro):
            if remove_reaction:
                await key.remove_reaction(self.emoji, self.client.user)
            self.coro[key].cancel()
            del self.coro[key]
