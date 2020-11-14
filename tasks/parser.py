import logging
import re
from tasks.music.player import Player

async def message(message, profile):
    logging.info('Parsing message from [{1.name}]{0.author}: {0.content}'.format(message, profile.guild))

    youtube = re.compile('(?:youtube(?:-nocookie)?\\.com\\/(?:[^\\/\n\\s]+\\/\\S+\\/|(?:v|vi|e(?:mbed)?)\\/|\\S*?[?&]v=|\\S*?[?&]vi=)|youtu\\.be\\/)([a-zA-Z0-9_-]{11})')
    
    match = youtube.findall(message.content)
    if match:
        youtube_id = match[0]
        base_url = 'https://www.youtube.com/watch?v='
        normalized_url = base_url+youtube_id
        channel = message.guild.voice_channels[0]

        await profile.player.connect(channel)
        await profile.player.play_youtube(normalized_url)