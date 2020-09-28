import discord
import logging
import asyncio

def valid_channels(guild):
    verified_channels = 0
    hashed_channel = None
    for channel in guild.text_channels:
        logging.debug("Checking text channel: {}".format(channel))
        if channel.topic:
            if channel.topic.split()[-1] == str(hash(channel)):
                if verified_channels < 1:
                    verified_channels += 1
                    hashed_channel = channel
                else:
                    return None
    return hashed_channel

async def notify_not_setup(guild, client):
    text_channel = guild.text_channels[0]
    err_str = '⚠️Need to create new text channel.'
    message_warning = await text_channel.send(err_str + '\n**Click on the toolbox below to finish setup!**')
    await message_warning.add_reaction('🧰')
    
    def check(reaction, user):
        return user != client.user and str(reaction.emoji) == '🧰'

    try:
        # Note: Using reaction_add event, which only gets exec when reactions are added to a message in bot cache
        reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await message_warning.edit(content=err_str+'\n~~Click on the toolbox below to finish setup!~~')
        await text_channel.send('No reaction was sent. Leaving the server. Please add the bot again if you want to retry. https://discord.com/api/oauth2/authorize?client_id=758005098042622194&permissions=8&scope=bot')
        await guild.leave()
    else:
        await message_warning.edit(content=err_str+'\n**Creating the new text channel \"music-box\"**')