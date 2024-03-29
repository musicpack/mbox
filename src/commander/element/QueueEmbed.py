from discord.embeds import Embed

from src.constants import USAGE_TEXT
from src.music.element.Queue import Queue


class QueueEmbed(Embed):
    """Reperesents a Queue GUI object. Handles which MusicSource to play next and displays in the GUI."""

    def __init__(self, **kwargs) -> None:
        # Call super first so that it doesn't overwrite custom variables in this class
        super().__init__(**kwargs)

        self.title = "Queue"
        self.queue: Queue = kwargs.get("queue", None)
        self.radio: bool = kwargs.get("radio", False)

        if self.queue and len(self.queue.playlist) != 0:
            self.description = self.set_description()
        else:
            self.description = f"Nothing is in your queue. {USAGE_TEXT}"

    def set_description(self) -> str:
        """Update the queue Embed based on state."""
        description_now_playing = ""
        description_next = ""

        for index in range(self.queue.pos, len(self.queue.playlist)):
            title = self.queue.playlist[index].info["title"]
            webpage_url = self.queue.playlist[index].info["webpage_url"]
            embed = f"\n> {str(index+1)}. [{title}]({webpage_url})"
            if self.queue.pos == index:
                description_now_playing += embed
            else:
                description_next += embed

        if self.radio:
            self.set_footer(text="📻 Radio Mode")
            if description_next == "":
                description_next = "\nPress ⏭️ to generate next radio song. `/radio` to disable."

        if description_now_playing:
            description = "**Now Playing**" + description_now_playing
            if description_next:
                description += "\n" + "**Next**" + description_next

            return description

        return ""

    def __eq__(self, o: object) -> bool:
        def ordered_eval():
            yield self.description == o.description
            yield self.title == o.title

        return all(ordered_eval()) if type(o) == QueueEmbed else False
