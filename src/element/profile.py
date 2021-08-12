from discord.channel import TextChannel
from discord.client import Client
from discord.guild import Guild

from src.config import FFMPEG_PATH
from src.music.player import Player


class Profile:
    """Base class function representing one server. Creates a player object that manages the gui state of the command channel

    Args:
        guild (discord.Guild): The server this profile is tracking
        command_channel (List[discord.TextChannel], discord.TextChannel, optional): The text channel that the profile should track for commands.
    """

    def __init__(
        self, guild: Guild, command_channel: TextChannel, client: Client
    ) -> None:
        self.guild = guild
        self.command_channel = command_channel
        self.player: Player = Player(ffmpeg_path=FFMPEG_PATH, client=client)

    async def setup(self):
        """Setup varaibles nessasary for runtime"""
        await self.player.register_command_channel(
            command_channel=self.command_channel
        )

    async def cleanup(self):
        """Prepares class variables for deletion. Usually used to cancel asyncio tasks"""
        await self.player.cleanup()
