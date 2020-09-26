import discord
import logging

def valid_channels(guild):
    verified_channels = 0
    hashed_channel = None
    for channel in guild.text_channels:
        logging.debug("Checking text channel: {}".format(channel))
        if channel.topic.split()[-1] == str(hash(channel)):
            if verified_channels < 1:
                verified_channels += 1
                hashed_channel = channel
            else:
                return None
    return hashed_channel
