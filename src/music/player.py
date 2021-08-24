import asyncio
import logging
import random
import threading
from datetime import timedelta
from typing import Dict

import youtube_dl
from discord.channel import VoiceChannel
from discord.client import Client
from discord.player import FFmpegPCMAudio
from discord.voice_client import VoiceClient

from src.config import FFMPEG_PATH, MAX_CACHESIZE
from src.constants import YOUTUBE_ICON
from src.music.element.MusicSource import MusicSource
from src.music.element.Queue import Queue
from src.music.lyrics import youtube_lyrics


class Player:
    def __init__(
        self, ffmpeg_path, client: Client, guild_id: int, volume: int = 50
    ) -> None:
        self.connected_client: VoiceClient = None
        self.client = client
        self.guild_id = guild_id

        self.ffmpeg_path = ffmpeg_path
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
        self.ydl_opts = {"format": "bestaudio/worst"}

        # Lyrics Metadata
        self.default_lyrics_metadata()

        # Queue Metadata
        self.default_queue_metadata()

        # Player Metadata & Footer Metadata
        self.default_player_metadata()
        # Footer Metadata
        self.volume: int = volume
        self.ms_displayed = 0

    async def play(self, audio: MusicSource) -> None:
        """Plays the given MusicSource. Updates embeds if exists. Connect to the voicechannel before running function."""
        if self.connected_client and self.connected_client.is_connected():

            self.paused = False
            self.ms_displayed = -1

            # Make sure the MusicSource is back at 0:00 preventing us from playing a song from the middle.
            audio.reset()
            # Apply player volume to the audio source
            audio.volume = self.volume / 100

            if self.connected_client.is_playing():
                self.connected_client.source = audio
            else:
                self.connected_client.play(
                    source=audio, after=self.on_finished
                )

            # Lyrics metadata
            self.lyrics, self.lyrics_source = youtube_lyrics(audio.info["id"])
            # Player metadata
            self.playhead = timedelta(seconds=0)
            self.display_description = False
            self.resolved = audio.resolved
            self.from_file = False  # file is from_file but this variable is meant for a file just downloaded to disk
            self.sponsorblock: bool = None
            self.set_metadata(audio.info)

    def stop(self) -> None:
        """Stops song and disconnects from the voicechannel."""
        if self.connected_client:
            self.connected_client.stop()

            if self.connected_client.is_connected():
                asyncio.run_coroutine_threadsafe(
                    self.disconnect(), self.client.loop
                )

            # Lyrics metadata
            self.default_lyrics_metadata()
            # Queue metadata
            self.default_queue_metadata()
            # Player metadata
            self.default_player_metadata()

            self.cleanup()

    async def raise_volume(self):
        """Increases the volume by 10 if the volume is not >=200."""
        if not self.volume >= 200:
            self.volume += 10

        if (
            self.connected_client
            and self.connected_client.source
            and self.connected_client.is_connected()
        ):
            self.connected_client.source.volume = self.volume / 100

    async def lower_volume(self):
        """Decreases the volume by 10 if the volume is not <=0."""
        if not self.volume <= 0:
            self.volume -= 10

        if (
            self.connected_client
            and self.connected_client.source
            and self.connected_client.is_connected()
        ):
            self.connected_client.source.volume = self.volume / 100

    def pause(self):
        """Pauses the song"""
        self.paused = True
        if self.connected_client:
            self.connected_client.pause()

    def resume(self):
        """Resumes the currenly set song."""
        self.paused = False
        if self.connected_client:
            self.connected_client.resume()

    ########## Queue ##########
    def get_by_index(self, index) -> MusicSource:
        try:
            music_source = self.queue.get_by_index(index)
        except IndexError:
            logging.info("Given index does not exist!")
            return None
        else:
            music_source.reset()
            asyncio.run_coroutine_threadsafe(
                self.play(music_source), self.client.loop
            )
            return music_source

    def next(self) -> MusicSource:
        """Loads up the next song in the queue"""
        try:
            music_source = self.queue.next()
        except IndexError:
            logging.info("No more music to play. Stopping...")
            self.stop()
            return None
        else:
            asyncio.run_coroutine_threadsafe(
                self.play(music_source), self.client.loop
            )
            return music_source

    def last(self) -> MusicSource:
        """Loads up the previous song in the queue."""
        try:
            music_source = self.queue.prev()
        except IndexError:
            logging.info("Queue cant go back any further")
            return None
        else:
            asyncio.run_coroutine_threadsafe(
                self.play(music_source), self.client.loop
            )
            return music_source

    async def connect(self, channel: VoiceChannel):
        """Connects the player to a voicechannel"""
        if self.connected_client and self.connected_client.is_connected():
            logging.warn(
                "Player is already connected to channel {0.name}".format(
                    self.connected_client.channel
                )
            )
            return
        self.connected_client = await channel.connect()

        # Reset metadata for player
        self.default_lyrics_metadata()
        self.default_queue_metadata()
        self.default_player_metadata()

    async def disconnect(self):
        """Disconnects the player to a voicechannel"""
        if (
            self.connected_client is None
            or not self.connected_client.is_connected()
        ):
            logging.warn(
                "Player is not connected. Was it disconnected forcefully?"
            )
            return
        await self.connected_client.disconnect()

        self.connected_client = None

        # Reset metadata for player
        self.default_lyrics_metadata()
        self.default_queue_metadata()
        self.default_player_metadata()

    def delete_player(self, guild_id: int):
        # Placeholder function to be overwritten by superclass
        pass

    ########## MusicSource Event Handlers ##########
    def on_finished(self, error):
        if error:
            logging.exception("Error when finished playing: ", exc_info=error)
            self.stop()
        else:
            logging.debug("Finished playing song")
            try:
                # TODO change race condiiton for main look to check if on_finished exec because of disconnect or next song
                self.next()
            except IndexError:
                pass

    def on_read(self, ms, non_music):
        self.playhead = timedelta(milliseconds=ms)
        if non_music:
            self.sponsorblock = True
            self.ms_displayed = 14000
        if self.ms_displayed > 0:
            self.ms_displayed -= 20
        if (
            ms % 14000 == 0 and not non_music
        ) or self.ms_displayed == 13960:  # 13960 represents the point where ms_displayed starts decrementing
            if self.ms_displayed == 0:
                self.sponsorblock = False
                self.ms_displayed = (
                    -1
                )  # make negative to avoid line above assignment multiple times

    ########## High Level Helper Functions ##########
    async def play_youtube(self, link: str):
        if self.connected_client and self.connected_client.is_connected():
            # if not grab info to add for streaming queue
            with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                video_info: dict = ydl.extract_info(link, download=False)
                source: str = video_info["formats"][0][
                    "url"
                ]  # take the first result given from youtube
                raw_audio_source = FFmpegPCMAudio(
                    executable=FFMPEG_PATH,
                    source=source,
                    **self.FFMPEG_OPTIONS
                )
                audio = MusicSource(
                    raw_audio_source, info=video_info, volume=self.volume / 100
                )

                self.queue.add(audio)

                # If the player is not playing because it just came in to the channel (not because of being paused), advance the track head to the next (just added) song
                if (
                    not self.connected_client.is_playing()
                    and not self.connected_client.is_paused()
                ):
                    if len(self.queue.playlist) == 1:
                        await self.play(self.queue.current())
                    else:
                        self.next()

                @audio.event
                def on_read(ms, non_music):
                    self.on_read(ms, non_music)

                # Determine if video is cacheable
                if not video_info[
                    "is_live"
                ]:  # TODO Player should show that the video is live in the GUI
                    if video_info[
                        "filesize"
                    ]:  # TODO add handling when video_info['filesize'] is not found/supported by youtube_dl
                        do_cache = (
                            True
                            if video_info["filesize"] <= MAX_CACHESIZE
                            else False
                        )

                        # Using threading library in order to prevent youtube_dl from blocking asyncio loops
                        threading.Thread(
                            target=lambda: audio.resolve(cache=do_cache)
                        ).start()

                    @audio.event
                    def on_resolve(info, path):
                        if (
                            self.queue.current()
                            and self.queue.current().info == info
                        ):
                            self.from_file = True
                            self.resolved = False  # Resolved is false to display the special status 'from_file'

        else:
            logging.error("Can't play_youtube() without connecting first")

    def cleanup(self):
        """Used when this player instance is about to be deleted.
        Tasks:
        - Clean up audio sources from queue
        - Delete player object instances from superclass
        """
        # Cleanly shut down ffmpeg instances and delete temporary files from the Queue
        for audio in self.queue.playlist:
            audio.cleanup()
            audio.remove_temp_file()

        self.delete_player(guild_id=self.guild_id)

    ########## Lyrics ##########
    def default_lyrics_metadata(self) -> None:
        """Sets the lyrics metadata variables to default values"""
        self.lyrics = None
        self.lyrics_source: str = None

    ########## Queue ##########
    def default_queue_metadata(self) -> None:
        """Sets the queue metadata variables to default values"""
        self.queue = Queue()

    ########## Player ##########

    def default_player_metadata(self) -> None:
        """Sets the player metadata variables to default values.
        Note: Since footer is part of player, it will be reset as well."""

        # Player metadata
        self.display_description: str = False
        self.video_title: str = None
        self.video_url: str = None
        self.video_description: str = None
        self.video_uploader: str = None
        self.video_uploader_url: str = None
        self.video_thumbnail: str = None

        # Footer metadata
        self.icon_url: str = None
        self.resolved = False
        self.from_file = False

        self.paused: bool = None
        self.video_source: str = None
        self.playhead: timedelta = None
        self.duration: timedelta = None
        self.sponsorblock: bool = None

    async def toggle_display_description(self):
        """Intake function for 💬 emoji reaction on_press event"""
        self.display_description = not self.display_description

    async def on_play_pause(self):
        """Intake function for ⏯ emoji reaction on_press event"""
        if self.connected_client:
            if self.connected_client.is_playing():
                self.pause()
            elif self.connected_client.is_paused():
                self.resume()

    async def shuffle(self):
        if self.connected_client:
            playlist = self.queue.playlist
            pos = self.queue.pos
            next_songs = playlist[(pos + 1) :]
            if self.queue.pos < len(self.queue.playlist) - 1:
                random.shuffle(next_songs)
                self.queue.playlist = (
                    playlist[:pos] + [playlist[pos]] + next_songs
                )
            else:
                raise IndexError("No more songs in the queue to shuffle")

    ########## General Helper Functions ##########
    def metadata_youtube_dl(self, info: dict) -> Dict[str, str]:
        """Parses youtube_dl dictionary to standard mbox naming format.

        Args:
            info (dict): youtube_dl dictionary format

        Returns:
            dict: Implements the following metadata fields
                video_title: str
                video_url: str
                video_description: str
                video_uploader: str
                video_uploader_url: str
                video_thumbnail: str
                icon_url: str
                video_source: str
                duration: timedelta
        """

        return {
            "video_title": info["title"],
            "video_url": info["webpage_url"],
            "video_description": info["description"],
            "video_uploader": info["uploader"],
            "video_uploader_url": info["uploader_url"],
            "video_thumbnail": info["thumbnail"],
            "icon_url": YOUTUBE_ICON,
            "video_source": "Youtube",
            "duration": timedelta(seconds=info["duration"]),
        }

    def set_metadata(self, info: dict) -> None:
        """sets metadata attributes to self

        Args:
            info (dict): youtube_dl dict
        """
        metadata_dict = self.metadata_youtube_dl(info)
        for metadata_name, value in metadata_dict.items():
            setattr(self, metadata_name, value)
