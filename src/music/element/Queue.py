from typing import List

from src.music.element.MusicSource import MusicSource
from src.constants import *


class Queue:
    """Reperesents a Queue GUI object. Handles which MusicSource to play next."""
    def __init__(self, playlist: List[MusicSource] = None) -> None:
        if playlist:
            self.playlist = playlist
        else:
            self.playlist = []

        self.index = None
        self.at_beginning = False
        self.at_end = False

    def remove_index(self, index: int):
        """Removes a song from a list."""
        return self.playlist.pop(index)

    def reset_all(self):
        """Removes all MusicSources from the queue"""
        for music in self.playlist:
            music.cleanup()  # TODO: Handle if the cleanup failes in error because the code below it will not run
        self.playlist = []
        self.index = None
        self.at_beginning = True
        self.at_end = False

    async def reset_next_playing(self):
        """Removes all but the current queued song from the list"""
        self.playlist = self.playlist[:self.index+1]

    def add(self, music) -> None:
        """Add a MusicSource to the music queue."""
        self.playlist.append(music)

    def current(self):
        """Get the currently playing MusicSource"""
        if self.playlist:
            if self.index == None:
                return None
            else:
                return self.playlist[self.index]
        return None

    def next(self) -> MusicSource:
        """Get the next MusicSource and change the head to the next MusicSource."""
        if self.playlist:
            if self.at_beginning or self.index == None:
                self.index = 0
                self.at_beginning = False
                return self.playlist[self.index]
            elif self.index + 1 < len(self.playlist):
                self.at_end = False
                self.index += 1
                return self.playlist[self.index]
            else:
                self.at_end = True
                raise IndexError('At the end')
        raise IndexError('MusicQueue list empty')

    def prev(self) -> MusicSource:
        """Get the previous MusicSource and changes the head to the previous MusicSource. Updates the Embed."""
        if self.playlist:
            if self.at_end:
                self.at_end = False
                return self.playlist[self.index]
            elif self.index - 1 >= 0:
                self.index -= 1
                return self.playlist[self.index]
            else:
                raise IndexError('Queue index corrupted')
        raise IndexError('MusicQueue list empty')
