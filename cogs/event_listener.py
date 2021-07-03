import os
from typing import List, Union

import discord
from discord.ext import commands
from src.lib import dynamodb
import src.preinitialization
from config import TOKEN
from main import bot, logging
from src.auth import Auth, Crypto
from src.command_handler import play_ytid
from src.constants import INVITE_LINK_FORMAT
from src.element.MusicBoxContext import MusicBoxContext
from src.element.profile import Profile
from src.parser import parse

COMMAND_CHANNEL_WARNING = "Accepted command."
watching_channels = []
profiles: List[src.element.profile.Profile] = []
dynamoDB = dynamodb.Dynamodb()


class EventListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Generate a rsa keychain
        self.crypto = Crypto()

        # Check if a public/private keychain exists already
        public_key_path = "mbox_public.key"
        private_key_path = "mbox_private.key"

        if self.crypto.both_exist(
            os.path.isfile(public_key_path), os.path.isfile(private_key_path)
        ):
            logging.info("Loaded public and private keys from file.")
            self.crypto.load_keys(public_key_path, private_key_path)
        else:
            logging.info("Generated new public and private keys.")
            self.crypto.generate_keys()
            self.crypto.save_keys()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        logging.debug("Message from {0.author}: {0.content}".format(message))

        # Ignore message if it was from a bot
        if message.author == bot.user:
            return

        # check if item already exists in memory 
        requested_item = dynamoDB.guild_item_exists_in_memory(self.bot.user.id)

        # Retreve guild item from database using application id if item does not exists in memory
        if(not requested_item):
            get_response: dict = dynamoDB.retrieve_guild_item(self.bot.user.id),
            logging.info(f'printing get response from dynamo: {get_response}')
        else:
            logging.info("getting info from in memory object")
            logging.info(f'Object in memory: {requested_item}')


        #TODO: still using profiles right now (will be removed once MusicBoxContext is refactored)
        
        # Check which profile the message relates to
        for profile in profiles:
            if profile.guild == message.guild:
                
                #TODO Check if its from a command channel 
                # Check if the message comes from a command channel
                if profile.command_channel == message.channel:
                    await message.delete()

                    # Ignore message if it came from a bot that was not from a webhook
                    if message.author.bot and not message.webhook_id:
                        return

                    # Top level command stop
                    if message.content == "stop":
                        logging.info(
                            "Received stop from {0.name}".format(
                                message.author
                            )
                        )
                        await bot.logout()

                    # Create a context
                    bot_ctx = MusicBoxContext(
                        prefix="",
                        profile=profile,
                        name="",
                        slash_context=None,
                        message=message,
                        args=[message.content],
                        kwargs={"command": message.content},
                    )

                    # Top level command play
                    if message.content == "play":
                        logging.info(
                            "Received play from {0.name}".format(
                                message.author
                            )
                        )
                        await play_ytid("JwmGruvGt_I", bot_ctx)
                        break

                    await parse(bot_ctx)
                    break

                # Check if the message came from a admin channel
                elif Auth.is_admin_channel(
                    channel=message.channel, token=TOKEN, crypto=self.crypto
                ):
                    argv = message.content.split()
                    # Create a context
                    bot_ctx = MusicBoxContext(
                        prefix="",
                        profile=profile,
                        name="admin",
                        slash_context=None,
                        message=message,
                        args=argv,
                        kwargs={"command": message.content},
                        bot=self.bot,
                        crypto=self.crypto,
                    )

                    await parse(bot_ctx)
                    break

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        logging.debug("Typing from {0.name}".format(user))

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):

        # Adding guild item to database first time bot joins server
        put_response: dict = dynamoDB.store_guild_item(self.bot.user.id , guild.id,)
        logging.info(f'Printing response from Dynamo: {put_response}')
        logging.info(f'Joined Server: {guild.name}')
        await guild.text_channels[0].send('Thanks for adding Music Bot!')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        #Remove guild item from database
        delete_response: dict = dynamoDB.delete_guild_item(self.bot.user.id)
        logging.info(f'Printing response from Dynamo: {delete_response}')
        logging.info('Removed from Server: {0.name}'.format(guild))

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
                for profile in profiles:
                    if profile.guild == member.guild:
                        profile.player.stop()

    @commands.Cog.listener()
    async def on_ready(self):
        await src.preinitialization.generate_profiles(
            bot.guilds, self.bot, profiles
        )
        for profile in profiles:
            await profile.setup()
        logging.info("Music Box is all set up and ready to go!")


def setup(bot):
    bot.add_cog(EventListener(bot))
