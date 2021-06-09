from discord.embeds import Embed

from src.music.element.Queue import Queue
from src.constants import *


class QueueEmbed (Embed):
    """Reperesents a Queue GUI object. Handles which MusicSource to play next and displays in the GUI."""

    def __init__(self, **kwargs) -> None:
        # Call super first so that it doesn't overwrite custom variables in this class
        super().__init__(**kwargs)

        self.title = 'Queue'
        self.queue: Queue = kwargs.get('queue', None)


        if self.queue and self.queue.index != None:
            self.description = self.get_description()
        else:
            self.description = f'Nothing is in your queue. {USAGE_TEXT}'

    def get_description(self) -> str:
        """Update the queue Embed based on state."""
        text_np = '**Now Playing**'
        text_n = '**Next**'
        description_np = ''
        description_n = ''

        for index in range(self.queue.index, len(self.queue.playlist)):
            if self.queue.index == index:
                description_np += '\n> [' + self.queue.playlist[index].info['title'] + \
                    '](' + self.queue.playlist[index].info['webpage_url'] + ')'
            else:
                description_n += '\n> [' + self.queue.playlist[index].info['title'] + \
                    '](' + self.queue.playlist[index].info['webpage_url'] + ')'

        if description_np:
            description = text_np + description_np
            if description_n:
                description += '\n' + text_n + description_n

            return description
        
        return ''
