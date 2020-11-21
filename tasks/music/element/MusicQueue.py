import asyncio
from tasks.music.element.MusicSource import MusicSource
from tasks.commander.element.ChatEmbed import ChatEmbed
class MusicQueue:
    def __init__(self, active_embed: ChatEmbed, list: list[MusicSource] = []) -> None:
        self.list = list
        self.index = None
        self.buttons = {}
        self.ChatEmbed = active_embed
        if not list:
            self.at_beginning = True
            self.at_end = False
        self.at_beginning = False
        self.at_end = False
    
    async def setup(self):
        self.ChatEmbed.actions = list(self.buttons.values())
        self.ChatEmbed.embed.title = 'Empty Queue'
        await self.ChatEmbed.update()

    def remove_index(self, index: int):
        return self.list.pop(index)
    
    def reset_all(self):
        pass

    async def update_embed_from_queue(self) -> None:
        title = 'Queue Empty'
        if self.at_end:
            self.ChatEmbed.embed.description = 'No Song Playing'
            self.ChatEmbed.embed.title = title
            await self.ChatEmbed.update()
            return

        text_np = '**Now Playing**'
        text_n = '**Next**'
        description_np = ''
        description_n = ''

        
        for index in range(self.index, len(self.list)):
            if self.index == index:
                title = 'Queue'
                description_np += '\n> [' + self.list[index].info['title'] + '](' + self.list[index].info['webpage_url'] + ')'
            else:
                description_n += '\n> [' + self.list[index].info['title'] + '](' + self.list[index].info['webpage_url'] + ')'
        
        if description_np:
            self.ChatEmbed.embed.title = title

            description = text_np + description_np
            if description_n:
                description += '\n' + text_n + description_n

            self.ChatEmbed.embed.description = description
            await self.ChatEmbed.update()

    def add(self, music) -> None:
        self.list.append(music)
        asyncio.create_task(asyncio.coroutine(self.update_embed_from_queue)())

    
    def current(self):
        if self.list:
            if self.index == None:
                return None
            else:
                return self.list[self.index]
        return None
        

    def next(self) -> MusicSource:
        if self.list:
            if self.at_beginning or self.index == None:
                self.index = 0
                self.at_beginning = False
                return self.list[self.index]
            elif self.index + 1 < len(self.list):
                self.at_end = False
                self.index += 1
                return self.list[self.index]
            else:
                self.at_end = True
                return None
        raise IndexError('MusicQueue list empty')

    def prev(self):
        if self.list:
            if self.at_end:
                self.at_end = False
                return self.list[self.index]
            elif self.index - 1 >= 0:
                self.index -= 1
                return self.list[self.index]
            else:
                return None
        raise IndexError('MusicQueue list empty')