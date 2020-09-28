import logging
import tasks.messenger

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

async def validate_server(guild, client):
    logging.debug('Checking guild [{}] is set up'.format(guild))
    hashed_channels = valid_channels(guild)
    if len(hashed_channels) == 0: 
        logging.debug('Guild [{}] is not set up. Sending request to set up.'.format(guild))
        err_msg = '⚠️Need to create new text channel.'
        act_msg = 'Created the new text channel \'music-box\''
        
        async def action(guild, client):
            music_box = await guild.create_text_channel(name='music-box')
            topic = 'Music Box controlled channel. Chat in this channel will be deleted. Version 0.1 ' + str(hash(music_box))
            await music_box.edit(topic=topic)
        
        await tasks.messenger.notify_action_required(guild, client, err_msg, action, act_msg)
        return False
    elif len(hashed_channels) > 1:
        logging.debug('Guild [{}] has too many valid channels. Sending request to fix.'.format(guild))
        offending_channels = []
        for channel in hashed_channels:
            offending_channels.append(channel.name)
        err_msg = '⚠️Need to remove topic of channels: ' + str(offending_channels)
        act_msg = 'Removed topic of all valid channels and created a new channel'
        
        async def action(guild, client):
            for channel in hashed_channels:
                await channel.edit(topic='')
            music_box = await guild.create_text_channel(name='music-box')
            topic = 'Music Box controlled channel. Chat in this channel will be deleted. Version 0.1 ' + str(hash(music_box))
            await music_box.edit(topic=topic)

        await tasks.messenger.notify_action_required(guild, client, err_msg, action, act_msg)
        return False
    return True
