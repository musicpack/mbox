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
            # 'next_track': Button(emoji='⏭️', client = self.client, action=self.next),
            # 'lower_volume': Button(emoji='🔉', client = self.client, action=self.lower_volume),
            # 'raise_volume': Button(emoji='🔊', client = self.client, action=self.raise_volume),
            # 'toggle_description': Button(emoji='💬', client = self.client, action=self.toggle_description)
        }
        
        self.ChatEmbed = None
    
    async def setup(self):
        self.ChatEmbed = self.messenger.gui['reporter']
        self.ChatEmbed.actions = list(self.buttons.values())
        await self.ChatEmbed.update()
    
    async def logout(self):
        await self.client.logout()

    async def refresh(self):
        await self.profile.setup()
