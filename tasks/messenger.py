import asyncio

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