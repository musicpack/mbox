import logging
import re
import tasks.player

async def message(message):
    logging.info('Parsing message from {0.author}: {0.content}'.format(message))
    youtube = re.compile('(?:youtube(?:-nocookie)?\\.com\\/(?:[^\\/\n\\s]+\\/\\S+\\/|(?:v|vi|e(?:mbed)?)\\/|\\S*?[?&]v=|\\S*?[?&]vi=)|youtu\\.be\\/)([a-zA-Z0-9_-]{11})')
    
    match = youtube.findall(message.content)
    if match:
        youtube_id = match[0]
        base_url = 'https://www.youtube.com/watch?v='
        normalized_url = base_url+youtube_id
        channel = message.guild.voice_channels[0]
        await tasks.player.play_youtube(channel, normalized_url)