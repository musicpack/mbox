import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# Discord setup
token = os.getenv("DISCORD_TOKEN", "")
guild_id = int(os.getenv("DISCORD_GUILD", ""))
