import logging
from datetime import datetime
from typing import List

from discord import ClientException, Guild, Message, TextChannel
from discord.client import Client

from src.constants import VERSION
from src.element.profile import Profile


def valid_channels(guild: Guild):
    verified_channels = 0
    hashed_channel = []
    for channel in guild.text_channels:
        logging.debug(
            "Checking text channel: {}: {}".format(channel, str(hash(channel)))
        )
        if channel.topic:
            if channel.topic.split()[-1] == str(hash(channel)):
                verified_channels += 1
                hashed_channel.append(channel)
    return hashed_channel


def get_expected_topic(text_channel: TextChannel) -> str:
    return f"Music Box controlled channel. Chat in this channel will be deleted. Version {VERSION} {str(hash(text_channel))}"


async def fix_topic(text_channel: TextChannel) -> None:
    """Update topic if out of date or malformed"""
    expected_topic = get_expected_topic(text_channel)

    if text_channel.topic != expected_topic:
        await text_channel.edit(topic=expected_topic)


async def create_command_channel(guild: Guild) -> TextChannel:
    music_box = await guild.create_text_channel(name="music-box")
    await music_box.edit(topic=get_expected_topic(music_box))
    return music_box


async def fix_duplicate_command_channels(
    guild: Guild, channels: List[TextChannel]
) -> TextChannel:
    logging.debug(
        f"Guild [{guild}] has too many valid channels. Sending request to fix."
    )
    for channel in channels:
        await channel.edit(
            topic="Old music-box command channel. Safe to delete."
        )

    return await create_command_channel(guild)


async def clean_chat(text_channel: TextChannel) -> None:
    """
    Removes all messages in the command channel to prepare for sending a gui.

    ## Raises

        ClientException – The number of messages to delete was more than 100.

        Forbidden – You do not have proper permissions to delete the messages or you’re not using a bot account.

        NotFound – If single delete, then the message was already deleted.

        HTTPException – Deleting the messages failed.
    """
    text_channel_messages: List[Message] = []
    message: Message
    async for message in text_channel.history(limit=101):
        if (datetime.today() - message.created_at).days > 14:
            raise ClientException(
                "Text channel contains messages older then 14 days."
            )
        if len(text_channel_messages) > 100:
            raise ClientException("Text channel contains over 100 messages.")

        text_channel_messages.append(message)

    logging.info(f"deleted_messages: {str(len(text_channel_messages))}")
    await text_channel.delete_messages(text_channel_messages)


#TODO we dont need this, but need to emulate the functionality of this method 
async def generate_profiles(
    guilds: List[Guild], client: Client, profiles: List[Profile]
) -> None:
    for server in guilds:
        channel_list = valid_channels(server)
        validated_channel = None

        if len(channel_list) == 1:
            validated_channel = channel_list[0]
        elif len(channel_list) > 1:
            validated_channel = await fix_duplicate_command_channels(
                server, channels=channel_list
            )
        else:
            validated_channel = await create_command_channel(server)

        try:
            await clean_chat(validated_channel)
        except ClientException:
            # there was a client problem removing messages in the textchannel, delete it instead
            await validated_channel.delete()
            validated_channel = create_command_channel(guild=server)
        finally:
            await fix_topic(validated_channel)
            profiles.append(
                Profile(
                    guild=server,
                    command_channel=validated_channel,
                    client=client,
                )
            )

    return profiles
