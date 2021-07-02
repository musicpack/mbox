import logging
import re

from src.command_handler import logout, play_ytid
from src.element.MusicBoxContext import MusicBoxContext
from src.search import youtube, youtube_music

YTRE = "(?:youtube(?:-nocookie)?\\.com\\/(?:[^\\/\n\\s]+\\/\\S+\\/|(?:v|vi|e(?:mbed)?)\\/|\\S*?[?&]v=|\\S*?[?&]vi=)|youtu\\.be\\/)([a-zA-Z0-9_-]{11})"
YOUTUBE_ID_REGEX = re.compile(YTRE)


# TODO make sure user input is sanitized
async def parse(context: MusicBoxContext) -> str:
    """Generic parse function. Takes in a context from a user input and does actions based on it.

    Args:
        context (Context): Context based on user input. Handles free form commands (no prefixes).
        Contexts generated from SlashCommands should be directed to src.SlashCommands

    Returns:
        str: Status message
    """
    logging.info(
        "Parsing context [{0}]{1}: {2}".format(
            context.get_guild(),
            context.get_author(),
            context.get_str_full_input(),
        )
    )

    # General bot command
    if (
        context.name == ""
        or context.name == "c"
        or context.name == "play"
        or context.name == "youtube"
    ):
        user_input = " ".join(context.args)

        match = YOUTUBE_ID_REGEX.findall(user_input)
        if match:
            youtube_id: str = match[0]
            await play_ytid(id=youtube_id, context=context)
        else:
            # search youtube for the phrase the user has typed
            if context.name == "youtube":
                youtube_id = youtube(user_input)
            else:
                youtube_id = youtube_music(user_input)
            if youtube_id:
                await play_ytid(youtube_id, context)
                return f"{user_input} accepted"
            else:
                if context.name == "youtube":
                    return f"Could not find a video named: {user_input}"
                else:
                    return f"Could not find a song named: {user_input}"

    elif context.name == "admin":
        if context.args[0] == "stop":
            await logout(context=context)
            return
        elif context.args[0] == "genkey":
            await genkey(context=context)
            return
        elif context.args[0] == "pubkey":
            await pubkey(context=context)
            return

    elif context.name == "dm":
        if context.args[0] == "genkey":
            await genkey(context=context)
            return
        elif context.args[0] == "pubkey":
            await pubkey(context=context)
            return

    return "Unknown commmand"
