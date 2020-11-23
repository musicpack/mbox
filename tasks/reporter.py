from tasks.commander.messenger import Messenger
from tasks.commander.element.Button import Button

class Reporter:
    def __init__(self, profile,  messenger: Messenger) -> None:
        self.messenger = messenger
        self.client = messenger.client
        self.profile = profile

        self.buttons = {
            'refresh': Button(emoji='🔄', client = self.client, action=self.refresh),
            'logout': Button(emoji='🟥', client = self.client, action=self.logout)
        }
        
        self.ChatEmbed = None
    
    async def setup(self):
        self.ChatEmbed = self.messenger.gui['reporter']
        self.ChatEmbed.actions = list(self.buttons.values())
        await self.ChatEmbed.update()
    
    async def logout(self):
        await self.client.logout()

    async def refresh(self):
        if self.profile.player.connected_client:
            if self.profile.player.connected_client.is_connected():
                self.profile.player.stop()
        await self.profile.setup()
