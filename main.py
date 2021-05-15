import rsa
from src.element.context import Context
from typing import List, Union
import discord
import sys
import logging

import src.preinitialization
import src.parser
import src.element.profile
from src.constants import *
from discord_slash import SlashCommand
from discord_slash.context import SlashContext
from discord_slash.utils.manage_commands import create_option

import src.auth
import base64, time, os.path, datetime
mbox = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(mbox, sync_commands=True) 

COMMAND_CHANNEL_WARNING = 'Accepted command.'

logging_level = logging.INFO
if len(sys.argv) > 1:
    if sys.argv[1] == 'debug':
        logging_level = logging.DEBUG

logging.basicConfig(
    level=logging_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log", encoding='utf8'),
        logging.StreamHandler()
    ]
)

watching_channels = []
profiles: List[src.element.profile.Profile] = []

## Crypto variables
crypto = src.auth.Crypto()

startup_epoch = int(time.time())
spent_epoch = 0

# Check if a public/private keychain exists already
public_key_path = 'mbox_public.key'
private_key_path = 'mbox_private.key'
if crypto.both_exist(os.path.isfile(public_key_path), os.path.isfile(private_key_path)):
    logging.info('Loaded public and private keys from file.')
    crypto.load_keys(public_key_path, private_key_path)
else:
    logging.info('Generated new public and private keys.')
    crypto.generate_keys()
    crypto.save_keys()

async def process_slash_command(ctx: SlashContext, f):
    for profile in profiles:
        if profile.guild == ctx.guild:
            mbox_ctx = Context(prefix='/',profile=profile,name=ctx.name,slash_context=ctx,message=ctx.message,args=ctx.args,kwargs=ctx.kwargs)
            if ctx.channel == profile.messenger.command_channel:
                await ctx.send(content=COMMAND_CHANNEL_WARNING)
                await f(mbox_ctx)
                await ctx.message.delete()
                return
            else:
                await ctx.defer(hidden=True)
                status = await f(mbox_ctx)
            break

    await ctx.send(content = f"{status}", hidden=True)

@slash.slash(name="c",
            description='General music-box command',
            options=[
               create_option(
                 name="command",
                 description="Input to message the bot as if sent to the command channel.",
                 option_type=3,
                 required=True
               )
             ])
async def _command(ctx: SlashContext, command: str):
    await process_slash_command(ctx, src.parser.message)

@slash.slash(name="pause",
            description='Pauses actively playing song')
async def _pause(ctx: SlashContext):
    await process_slash_command(ctx, src.parser.pause_player)

@slash.slash(name="next",
            description='Goes to the next song.')
async def _next(ctx: SlashContext):
    await process_slash_command(ctx, src.parser.player_next)
@slash.slash(name="skip",
            description='Goes to the next song.')
async def _skip(ctx: SlashContext):
    await process_slash_command(ctx, src.parser.player_next)

@slash.slash(name="prev",
            description='Goes to the previous song.')
async def _prev(ctx: SlashContext):
    await process_slash_command(ctx, src.parser.player_prev)
@slash.slash(name="back",
            description='Goes to the previous song.')
async def _back(ctx: SlashContext):
    await process_slash_command(ctx, src.parser.player_prev)

@slash.slash(name="Play",
            description='Plays or resumes a song.',
            options=[
               create_option(
                 name="song_name_or_link",
                 description="Adds this song to the queue.",
                 option_type=3,
                 required=False
               )
             ])
async def _play(ctx: SlashContext, song_name_or_link = None):
    if song_name_or_link:
        await process_slash_command(ctx, src.parser.message)
    else:
        await process_slash_command(ctx, src.parser.resume_player)
@slash.slash(name="Youtube",
            description='Add a youtube video to the queue.',
            options=[
               create_option(
                 name="search",
                 description="Name or link of a youtube video",
                 option_type=3,
                 required=True
               )
             ])
async def _youtube(ctx: SlashContext, search):
    await process_slash_command(ctx, src.parser.message)

@mbox.event
async def on_ready():
    logging.info('Logged on as {0.user}'.format(mbox))
    await src.preinitialization.generate_profiles(mbox.guilds, mbox, profiles)
    for profile in profiles:
        await profile.setup()

@mbox.event
async def on_typing(channel, user, when):
    logging.debug('Typing from {0.name}'.format(user))

@mbox.event
async def on_guild_join(guild: discord.Guild):
    logging.info(f'Joined Server: {guild.name}')
    try:
        await guild.text_channels[0].send('Thanks for adding Music Bot!')
        await src.preinitialization.generate_profile(guild, mbox, profiles)
        for profile in profiles:
            await profile.setup()
    except discord.errors.Forbidden:
        owner_member: discord.Member = guild.owner
        if owner_member:
            content = f"You or a member in server {guild.name} added me without the right permissions. Try adding me again with the link: " + INVITE_LINK_FORMAT.format(mbox.user.id)
            await owner_member.send(content=content)
        await guild.leave()

@mbox.event
async def on_guild_remove(guild):
    logging.info('Removed from Server: {0.name}'.format(guild))
    for profile in profiles:
        if profile.guild == guild:
            await profile.messenger.unregister_all()
            profiles.remove(profile)


@mbox.event
async def on_message(message: discord.Message):
    logging.debug('Message from {0.author}: {0.content}'.format(message))
    
    # Any message created by the bot itself should be deleted outside of this function.
    if message.author == mbox.user:
        return

    # Top level command stop
    if message.content == 'stop':
        logging.info('Received stop from {0.name}'.format(message.author))
        await mbox.logout()
    
    # Top level command pubkey
    if message.content == 'pubkey' and isinstance(message.channel, discord.DMChannel): # only accept this command in a dm.
        logging.info('Received pubkey from {0.name} in a dm'.format(message.author))

        # save public key in a base 64 encoded string
        pubkey_64 = base64.b64encode(crypto.pubkey.save_pkcs1()).decode("utf-8")
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
                    await message.reply(content=crypto.encrypt_token_x(argv[1], argv[2]))
                except Exception as e:
                    await message.reply(content=str(e))
                return

            await message.reply(content=crypto.encrypt_token_time(argv[1]))
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

                # Ignore the message if its from a foreign bot in a command channel.
                if message.author.bot and message.author != mbox.user:
                    return

                # Create a context
                mbox_ctx = Context(prefix='',profile=profile,name='',slash_context=None,message=message,args=[message.content],kwargs={'command': message.content})

                # Top level command test
                if message.content == 'test':
                    logging.info('Received test from {0.name}'.format(message.author))
                    await profile.messenger.gui['player'].update()
                    break
                # Top level command rem
                if message.content == 'rem':
                    logging.info('Received rem from {0.name}'.format(message.author))
                    for action in profile.messenger.gui['player'].actions:
                        await action.remove_all()
                    break
                # Top level command play
                if message.content == 'play':
                    logging.info('Received play from {0.name}'.format(message.author))
                    await src.parser.play_ytid('JwmGruvGt_I', mbox_ctx)
                    break
                
                await src.parser.message(mbox_ctx)
                break

            # Check if the message came from a admin channel
            elif isinstance(message.channel, discord.TextChannel) and src.auth.Auth.is_admin_channel(message.channel,TOKEN,crypto):
                
                # Check if the message is a webhook that has a embed that has a footer.
                if message.webhook_id and message.embeds and message.embeds[0].footer.text:
                    # Check if embed has the correct certificate
                    message_dt = message.created_at
                    message_timestamp = int(message_dt.replace(tzinfo=datetime.timezone.utc).timestamp())
                    try:
                        decrypt_token, timestamp = crypto.decrypt_token_x(message.embeds[0].footer.text)
                    except rsa.pkcs1.DecryptionError as e:
                        logging.info(f'{str(e)} at [{message.channel.guild}]{message.channel}: {message.author} message id:{message.id}. Is the key invalid?')
                        await message.reply(content="Validation failed")
                        return
                    
                    global spent_epoch
                    # Validated that the embed has the correct certificate
                    if TOKEN == decrypt_token and src.auth.Auth.validate_timestamp(decrypted_epoch=int(timestamp), message_epoch=message_timestamp, spent_epoch=spent_epoch, startup_epoch=startup_epoch, tolerance= TIMESTAMP_TOLERANCE):
                        spent_epoch = int(timestamp)
                        if message.embeds[0].title == "Stop Warning":
                            logging.warning("Bot was warned that it will be stopping soon from webhook.")
                            # TODO: add cleanup code and warnings to all profiles playing a song now.
                            await message.reply(content="Acknowledged")
                            return
                        if message.embeds[0].title == "Stop Order":
                            logging.warning("Bot is stopping now from webhook.")
                            await message.reply(content="Approved")
                            await mbox.logout()
                    else:
                        logging.warning("Validation failed")
                        await message.reply(content="Validation failed")
                        return

                # Top level admin command pubkey
                # Returns the current public key the bot is using.
                if message.content == 'pubkey':
                    logging.info('Received pubkey from {0.name}'.format(message.author))
                    pubkey_64 = base64.b64encode(crypto.pubkey.save_pkcs1()).decode("utf-8")
                    f = open('mbox_public.key', 'r')
                    await message.reply(content= pubkey_64, file=discord.File(f))
                    f.close()
                    return
                
                if 'genkey' in message.content:
                    argv = message.content.split()

                    if len(argv) > 1 and argv[1] != 'time':
                        try:
                            await message.reply(content=crypto.encrypt_token_x(TOKEN, argv[1]))
                        except Exception as e:
                            await message.reply(content=str(e))
                        return

                    await message.reply(content=crypto.encrypt_token_time(TOKEN))
                    return
                    
@mbox.event
async def on_reaction_add(reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
    if user != mbox.user:
        if reaction.message.author == mbox.user:
            await reaction.message.remove_reaction(reaction, user)

@mbox.event
async def on_voice_state_update(member, before, after):
    # Makes sure the player stops playing the song if the bot was disconnected by force
    if member == mbox.user:
        if before.channel and after.channel == None:
            for profile in profiles:
                if profile.guild == member.guild:
                    profile.player.stop()

mbox.run(TOKEN)
