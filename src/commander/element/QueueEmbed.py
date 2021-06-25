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


        if self.queue and self.queue.pos != None:
            self.description = self.set_description()
        else:
            self.description = f'Nothing is in your queue. {USAGE_TEXT}'

    def set_description(self) -> str:
        """Update the queue Embed based on state."""
        text_now_playing = '**Now Playing**'
        text_next = '**Next**'
        description_now_playing = ''
        description_next = ''

        for index in range(self.queue.pos, len(self.queue.playlist)):
            if self.queue.pos == index:
                description_now_playing += '\n> ' + str(index) + ". " + '[' + self.queue.playlist[index].info['title'] + \
                    '](' + self.queue.playlist[index].info['webpage_url'] + ')'
            else:
                description_next += '\n> ' + str(index) + ". " + '[' + self.queue.playlist[index].info['title'] + \
                    '](' + self.queue.playlist[index].info['webpage_url'] + ')'

        if description_now_playing:
            description = text_now_playing + description_now_playing
            if description_next:
                description += '\n' + text_next + description_next

            return description
        
        return ''
