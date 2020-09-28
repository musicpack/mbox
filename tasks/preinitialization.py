from os import truncate
import discord
import logging
import asyncio

def valid_channels(guild):
    verified_channels = 0
    hashed_channel = []
    for channel in guild.text_channels:
        logging.debug("Checking text channel: {}".format(channel))
        if channel.topic:
            if channel.topic.split()[-1] == str(hash(channel)):
                verified_channels += 1
                hashed_channel.append(channel)
    return hashed_channel

async def notify_action_required(guild, client, err_msg, action, act_msg):
    text_channel = guild.text_channels[0]
    err_str = err_msg
    message_warning = await text_channel.send(err_str + '\n**Click on the toolbox below to auto finish setup!**')
    await message_warning.add_reaction('🧰')
    
    def check(reaction, user):
        return user != client.user and str(reaction.emoji) == '🧰'

    try:
        # Note: Using reaction_add event, which only gets exec when reactions are added to a message in bot cache
        reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await message_warning.edit(content=err_str+'\n~~Click on the toolbox below to auto finish setup!~~')
        await text_channel.send('No reaction was sent. Leaving the server. Please add the bot again if you want to retry. https://discord.com/api/oauth2/authorize?client_id=758005098042622194&permissions=8&scope=bot')
        await guild.leave()
    else:
        await message_warning.edit(content=err_str+'\n' + '**' + act_msg + '**')
        await action(guild, client)

async def validate_server(guild, client):
    logging.debug('Checking guild [{}] is set up'.format(guild))
    hashed_channels = valid_channels(guild)
    if len(hashed_channels) == 0: 
        logging.debug('Guild [{}] is not set up. Sending request to set up.'.format(guild))
        err_msg = '⚠️Need to create new text channel.'
        act_msg = 'Creating the new text channel \'music-box\''
        
        async def action(guild, client):
            logging.info('action exec 0')
        
        await notify_action_required(guild, client, err_msg, action, act_msg)
        return False
    elif len(hashed_channels) > 1:
        logging.debug('Guild [{}] has too many valid channels. Sending request to fix.'.format(guild))
        offending_channels = []
        for channel in hashed_channels:
            offending_channels.append(channel.name)
        err_msg = '⚠️Need to remove topic of channels: ' + str(offending_channels)
        act_msg = 'Removing topic of all valid channels and creating a new channel'
        
        async def action(guild, client):
            logging.info('action exec 1')
        
        await notify_action_required(guild, client, err_msg, action, act_msg)
        return False
    return True
