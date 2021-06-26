from typing import List

from src.music.element.MusicSource import MusicSource
from src.constants import *


class Queue:
    """Reperesents a Queue GUI object. Handles which MusicSource to play next."""
    def __init__(self) -> None:
        self.playlist = []
        self.pos = 0

    def remove_index(self, index: int):
        """Removes a song from a list."""
        return self.playlist.pop(index)

    def reset_all(self):
        """Removes all MusicSources from the queue"""
        for music in self.playlist:
            music.cleanup()  # TODO: Handle if the cleanup failes in error because the code below it will not run
        self.playlist = []
        self.pos = 0

    async def reset_next_playing(self):
        """Removes all but the current queued song from the list"""
        self.playlist = self.playlist[:self.pos+1]

    def add(self, music) -> None:
        """Add a MusicSource to the music queue."""
        self.playlist.append(music)

    def current(self):
        """Get the currently playing MusicSource"""
        return self.playlist[self.pos]
    
    def get_by_index(self, index) -> MusicSource:
        if index >= 0:
            self.pos = index
            return self.playlist[index]
        raise IndexError("Index out of bound")

    def next(self) -> MusicSource:
        """Get the next MusicSource and change the head to the next MusicSource."""
        if len(self.playlist) == 0:
            raise IndexError('MusicQueue list empty')
        if self.pos + 1 < len(self.playlist):
            self.pos +=1
            return self.playlist[self.pos]
        raise IndexError('At the end')

    def prev(self) -> MusicSource:
        """Get the previous MusicSource and changes the head to the previous MusicSource. Updates the Embed."""
        if self.pos - 1 >= 0:
            self.pos -= 1
            return self.playlist[self.pos]
        raise IndexError('Index out of range')
