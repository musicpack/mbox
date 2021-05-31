import base64
import datetime
import time
import os

import rsa
import src.auth
from src.element.context import Context
from typing import Union, List
import discord
from main import bot, logging
import src.preinitialization
import src.parser
import src.element.profile
from discord_slash.utils.manage_commands import create_option
from discord.ext import commands
from src.constants import INVITE_LINK_FORMAT, TIMESTAMP_TOLERANCE
from config import TOKEN

COMMAND_CHANNEL_WARNING = 'Accepted command.'
watching_channels = []
profiles: List[src.element.profile.Profile] = []

class EventListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        ## Crypto variables
        self.crypto = src.auth.Crypto()

        self.startup_epoch = int(time.time())
        self.spent_epoch = 0

        # Check if a public/private keychain exists already
        public_key_path = 'mbox_public.key'
        private_key_path = 'mbox_private.key'
        if self.crypto.both_exist(os.path.isfile(public_key_path), os.path.isfile(private_key_path)):
            logging.info('Loaded public and private keys from file.')
            self.crypto.load_keys(public_key_path, private_key_path)
        else:
            logging.info('Generated new public and private keys.')
            self.crypto.generate_keys()
            self.crypto.save_keys()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        logging.debug('Message from {0.author}: {0.content}'.format(message))

        # Ignore message if it was from a bot
        if message.author == bot.user:
            return

        # Top level command stop
        if message.content == 'stop':
            logging.info('Received stop from {0.name}'.format(message.author))
            await bot.logout()
        
        # Top level command pubkey
        if message.content == 'pubkey' and isinstance(message.channel, discord.DMChannel): # only accept this command in a dm.
            logging.info('Received pubkey from {0.name} in a dm'.format(message.author))

            # save public key in a base 64 encoded string
            pubkey_64 = base64.b64encode(self.crypto.pubkey.save_pkcs1()).decode("utf-8")
            with open('mbox_public.key', 'r') as f:
                await message.reply(content= pubkey_64, file=discord.File(f))
                f.close()
            return
    
        # Top level command genkey
        if 'genkey' in message.content and isinstance(message.channel, discord.DMChannel):
            argv = message.content.split()

            if len(argv) > 1:
                if len(argv) > 2 and argv[2] != 'time':
                    try:
                        await message.reply(content=self.crypto.encrypt_token_x(argv[1], argv[2]))
                    except Exception as e:
                        await message.reply(content=str(e))
                    return

                await message.reply(content=self.crypto.encrypt_token_time(argv[1]))
                return
            else:
                await message.reply(content='genkey requires token argument in unauthenticated mode')
                return

        # Check which profile the message relates to
        for profile in profiles:
            if profile.guild == message.guild:

                # Check if the message comes from a command channel
                if profile.messenger.command_channel == message.channel:
                    await message.delete()

                    # Create a context
                    bot_ctx = Context(prefix='', profile=profile, name='', slash_context=None, message=message, args=[
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
                        await src.parser.play_ytid('JwmGruvGt_I', bot_ctx)
                        break

                    await src.parser.message(bot_ctx)
                    break

            # Check if the message came from a admin channel
            elif isinstance(message.channel, discord.TextChannel) and src.auth.Auth.is_admin_channel(message.channel,TOKEN,self.crypto):
                
                # Check if the message is a webhook that has a embed that has a footer.
                if message.webhook_id and message.embeds and message.embeds[0].footer.text:
                    # Check if embed has the correct certificate
                    message_dt = message.created_at
                    message_timestamp = int(message_dt.replace(tzinfo=datetime.timezone.utc).timestamp())
                    try:
                        decrypt_token, timestamp = self.crypto.decrypt_token_x(message.embeds[0].footer.text)
                    except rsa.pkcs1.DecryptionError as e:
                        logging.info(f'{str(e)} at [{message.channel.guild}]{message.channel}: {message.author} message id:{message.id}. Is the key invalid?')
                        await message.reply(content="Validation failed")
                        return
                    
                    # Validated that the embed has the correct certificate
                    if TOKEN == decrypt_token and src.auth.Auth.validate_timestamp(decrypted_epoch=int(timestamp), message_epoch=message_timestamp, spent_epoch=self.spent_epoch, startup_epoch=self.startup_epoch, tolerance=TIMESTAMP_TOLERANCE):
                        self.spent_epoch = int(timestamp)
                        if message.embeds[0].title == "Stop Warning":
                            logging.warning("Bot was warned that it will be stopping soon from webhook.")
                            # TODO: add cleanup code and warnings to all profiles playing a song now.
                            await message.reply(content="Acknowledged")
                            return
                        if message.embeds[0].title == "Stop Order":
                            logging.warning("Bot is stopping now from webhook.")
                            await message.reply(content="Approved")
                            await bot.logout()
                    else:
                        logging.warning("Validation failed")
                        await message.reply(content="Validation failed")
                        return

                # Top level admin command pubkey
                # Returns the current public key the bot is using.
                if message.content == 'pubkey':
                    logging.info('Received pubkey from {0.name}'.format(message.author))
                    pubkey_64 = base64.b64encode(self.crypto.pubkey.save_pkcs1()).decode("utf-8")
                    f = open('mbox_public.key', 'r')
                    await message.reply(content= pubkey_64, file=discord.File(f))
                    f.close()
                    return
                
                if 'genkey' in message.content:
                    argv = message.content.split()

                    if len(argv) > 1 and argv[1] != 'time':
                        try:
                            await message.reply(content=self.crypto.encrypt_token_x(TOKEN, argv[1]))
                        except Exception as e:
                            await message.reply(content=str(e))
                        return

                    await message.reply(content=self.crypto.encrypt_token_time(TOKEN))
                    return

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
