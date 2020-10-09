import asyncio

class Messenger:
    def __init__(self, default_channel, client, command_channel = None) -> None:
        self.default_channel = default_channel
        self.command_channel = command_channel
        self.client = client
        self.user = client.user
    
    async def notify_action_required(self, err_msg, action_failed, action_sucesss, act_msg):
        text_channel = self.default_channel
        err_str = err_msg
        message_warning = await text_channel.send(err_str + '\n**Click on the toolbox below to auto finish setup!**')
        await message_warning.add_reaction('🧰')
        
        def check(reaction, user):
            return user != self.user and str(reaction.emoji) == '🧰'

        try:
            # Note: Using reaction_add event, which only gets exec when reactions are added to a message in bot cache
            reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await message_warning.edit(content=err_str+'\n~~Click on the toolbox below to auto finish setup!~~')
            await action_failed(text_channel)
        else:
            await message_warning.edit(content=err_str+'\n' + '**' + act_msg + '**')
            await action_sucesss(text_channel)
