import logging
import src.commander.messenger
import src.element.profile
from typing import List



def valid_channels(guild):
    verified_channels = 0
    hashed_channel = []
    for channel in guild.text_channels:
        logging.debug("Checking text channel: {}: {}".format(channel,str(hash(channel))))
        if channel.topic:
            if channel.topic.split()[-1] == str(hash(channel)):
                verified_channels += 1
                hashed_channel.append(channel)
    return hashed_channel

async def generate_profiles(guilds, client, profiles = []):
    for server in guilds:
        hashed_channels = valid_channels(server)
        if len(hashed_channels) == 1:
            server_profile = src.element.profile.Profile(server, client, hashed_channels[0])
            profiles.append(server_profile)
        elif len(hashed_channels) > 1:
            server_profile = src.element.profile.Profile(server, client, hashed_channels)
            profiles.append(server_profile)
        else:
            server_profile = src.element.profile.Profile(server, client)
            profiles.append(server_profile)
    return True

async def generate_profile(guild, client, profiles = []):
    return await generate_profiles([guild], client, profiles)
