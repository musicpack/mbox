from datetime import timedelta
from typing import Callable

from discord.embeds import Embed, EmptyEmbed

from src.constants import USAGE_TEXT
from src.music.element.Queue import Queue


class PlayerEmbed(Embed):
    def __init__(self, **kwargs) -> None:
        # Call super first so that it doesn't overwrite custom variables in this class
        super().__init__(**kwargs)

        self.on_last: Callable = kwargs.get("on_last", None)
        self.on_play_pause: Callable = kwargs.get("on_play_pause", None)
        self.on_next: Callable = kwargs.get("on_next", None)
        self.on_lower_volume: Callable = kwargs.get("on_lower_volume", None)
        self.on_raise_volume: Callable = kwargs.get("on_raise_volume", None)
        self.on_toggle_description: Callable = kwargs.get(
            "on_toggle_description", None
        )

        # Footer Variables
        self.icon_url: str = kwargs.get("icon_url", EmptyEmbed)
        self.resolved: bool = kwargs.get("resolved", False)
        self.from_file: bool = kwargs.get("from_file", False)

        self.paused: bool = kwargs.get("paused", False)
        self.video_source: str = kwargs.get("video_source", None)
        self.volume: int = kwargs.get("volume", None)
        self.playhead: timedelta = kwargs.get("playhead", None)
        self.duration: timedelta = kwargs.get("duration", None)
        self.sponsorblock: bool = kwargs.get("sponsorblock", False)

        footer_text = self.generate_footer_text()
        icon_url = self.generate_icon_url()
        self.set_footer(text=footer_text, icon_url=icon_url)

        # Player Variables
        self.display_description: str = kwargs.get(
            "display_description", False
        )

        self.video_title: str = kwargs.get("video_title", None)
        self.video_url: str = kwargs.get("video_url", None)
        self.video_description: str = kwargs.get("video_description", None)
        self.video_uploader: str = kwargs.get("video_uploader", None)
        self.video_uploader_url: str = kwargs.get("video_uploader_url", None)
        self.video_thumbnail: str = kwargs.get("video_thumbnail", None)

        if self.video_title:
            self.title = self.video_title
            self.url = self.video_url
            self.description = self.get_video_description()
            self.set_author(
                name=self.video_uploader, url=self.video_uploader_url
            )
            self.set_thumbnail(url=self.video_thumbnail)
        else:
            self.title = "Player"
            self.description = f"Nothing is playing. {USAGE_TEXT}"

    def get_video_description(self) -> str:
        if self.video_description:
            if self.display_description:
                # TODO: Make button toggle multipage instead of just 2 pages
                return self.video_description[0:2048]
            else:
                list_description = self.video_description.splitlines()
                return "\n".join(list_description[0:3])
        else:
            return ""

    ########### FOOTER ############

    def update_footer_text(
        self,
        paused: bool = None,
        volume: int = None,
        playhead: timedelta = None,
        queue: Queue = None,
    ):
        """Generates new text and updates the footer text in Embed. Generates paused, volume, timeline states."""
        footer_text = self.generate_footer_text(
            paused=paused, volume=volume, playhead=playhead, queue=queue
        )

        self.embed.set_footer(
            text=footer_text, icon_url=self.footer["icon_url"]
        )

    def generate_footer_text(self) -> str or EmptyEmbed:
        """Generates footer text based on current infomation. Determines string output and order."""
        footer_list = []

        footer_list.append(self.get_paused())
        footer_list.append(self.get_source())
        footer_list.append(self.get_volume())
        footer_list.append(self.get_timeline())
        footer_list.append(self.get_sponsorblock())

        # remove empty strings ''
        footer_list[:] = [x for x in footer_list if x]

        if len(footer_list) == 0:
            return EmptyEmbed
        else:
            return " | ".join(footer_list)

    def generate_icon_url(self) -> str or EmptyEmbed:
        if not self.icon_url:
            return EmptyEmbed
        else:
            return self.icon_url

    def get_paused(self) -> str:
        """Gets a string formated paused value. Primarly for footer text."""

        return "PAUSED" if self.paused else ""

    def get_source(self) -> str:
        """Gets a string formated paused value. Primarly for footer text."""
        if type(self.video_source) == str:
            if self.from_file:
                return f"{self.video_source} 📁"
            elif self.resolved:
                return f"{self.video_source} 🗃️"
            else:
                return self.video_source
        else:
            return ""

    def get_volume(self) -> str:
        """Gets a string formated volume value. Primarly for footer text."""
        if self.volume is not None:
            emoji = "🔊"
            if self.volume <= 0:
                emoji = "🔇"
            elif self.volume <= 30:
                emoji = "🔈"
            elif self.volume <= 70:
                emoji = "🔉"
            else:
                emoji = "🔊"

            # TODO: Fix self.volume string when negative
            return emoji + str(self.volume / 100)[:3]
        else:
            return ""

    def get_timeline(self) -> str:
        # TODO: Fix so that playhead and duration generates strings independent of each other
        if self.playhead is not None and self.duration is not None:
            current = str(self.playhead)[:7]
            total = str(self.duration)[:7]
            if total[:2] == "0:":
                current = current[2:]
                total = total[2:]
            if total[:1] == "0":
                current = current[1:]
                total = total[1:]
            return current + "/" + total
        else:
            return ""

    def get_sponsorblock(self) -> str:
        if self.sponsorblock:
            return "✔️Skipped Non Music"
        else:
            return ""
