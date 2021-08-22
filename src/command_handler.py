import logging

from discord.voice_client import VoiceClient

from src.element.MusicBoxContext import MusicBoxContext


async def play_ytid(id: str, context: MusicBoxContext):
    """Loads a youtube id to the player

    Args:
        id (str): youtube video id
        context (Context): context object (src.MusicBoxContext version)
    """
    base_url = "https://www.youtube.com/watch?v="
    normalized_url = base_url + id
    voice_channel = context.determine_voice_channel()
    if voice_channel:
        await context.player.connect(voice_channel)
    await context.player.play_youtube(normalized_url)
    context.state.get_command_channel_panel(context.guild.id)
    await context.state.process_guild_panel(context.guild.id)


def get_player_client(context: MusicBoxContext) -> VoiceClient:
    if context.player.connected_client:
        if context.player.connected_client.is_connected():
            return context.player.connected_client


async def play_index(context: MusicBoxContext):
    if context.name == "play":
        p_client = get_player_client(context)
        index = int(context.slash_context.data["options"][0]["value"])

        if p_client:
            result = context.player.get_by_index(int(index) - 1)
            if result:
                await context.state.process_guild_panel(context.guild.id)
                return "Playing the selected song from the queue."
            return "Given index doesn't exist"
        return "Player not connected."

    logging.error("Context name play does not match function.")


async def player_prev(context: MusicBoxContext):
    if (
        context.name == "prev"
        or context.name == "back"
        or context.name == "prev_button"
    ):
        p_client = get_player_client(context)

        if p_client:
            result = context.player.last()
            if result:
                await context.state.process_guild_panel(context.guild.id)
                return "Playing previous song."
            return "No more songs to go back."
        return "Player not connected."

    logging.error("Context name prev/back does not match function.")


async def player_next(context: MusicBoxContext):
    if (
        context.name == "skip"
        or context.name == "next"
        or context.name == "next_button"
    ):
        p_client = get_player_client(context)

        if p_client:
            result = context.player.next()
            if result:
                await context.state.process_guild_panel(context.guild.id)
                return "Playing next song."
            return "Skipped. No more music to play."
        return "Player not connected."

    logging.error("Context name next/skip does not match function.")


async def pause_player(context: MusicBoxContext) -> str:
    if context.name == "pause":
        p_client = get_player_client(context)

        if p_client:
            if not p_client.is_paused():
                await context.player.on_play_pause()
                await context.state.process_guild_panel(context.guild.id)
                return "Paused player"
            return "Player is already paused"
        return "Player not connected"

    logging.error("Context name is not pause. Cannot pause player")


async def resume_player(context: MusicBoxContext) -> str:
    if context.name == "play":
        p_client = get_player_client(context)

        if p_client:
            if p_client.is_paused():
                await context.player.on_play_pause()
                await context.state.process_guild_panel(context.guild.id)
                return "Resumed player"
            return "Player is already playing"
        return "Player not connected"
    else:
        logging.error("Context name is not play. Cannot resume player")


async def logout(context: MusicBoxContext) -> None:
    # TODO: add cleanup code and warnings to all profiles playing a song now.
    await context.bot.logout()

    logging.error("Context name is not play. Cannot resume player")


async def shuffle_player(context: MusicBoxContext) -> str:
    if context.name == "shuffle":
        p_client = get_player_client(context)

        if p_client:
            try:
                await context.player.shuffle()
                await context.state.process_guild_panel(context.guild.id)
                return "Shuffled Player"
            except IndexError:
                return "No songs to shuffle."
        return "Player is not connected"

    logging.error("Context name is not shuffle. Cannot shuffle player")


async def lower_volume(context: MusicBoxContext) -> str:
    if context.name == "volume_down_button":
        await context.player.lower_volume()
        await context.state.process_guild_panel(context.guild.id)
        return "Volume decreased"

    logging.error("Context name is not lower_volume. Cannot lower_volume")


async def raise_volume(context: MusicBoxContext) -> str:
    if context.name == "volume_up_button":
        await context.player.raise_volume()
        await context.state.process_guild_panel(context.guild.id)
        return "Volume increased"

    logging.error("Context name is not raise_volume. Cannot raise_volume")


async def play_pause(context: MusicBoxContext) -> str:
    if context.name == "play_pause_button":
        await context.player.on_play_pause()
        await context.state.process_guild_panel(context.guild.id)
        return "Player toggled"

    logging.error("Context name is not play_pause. Cannot play_pause")
