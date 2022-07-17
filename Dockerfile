FROM python:3.7.10-slim-buster

ARG DiscordToken_mbox

# Set environment variables
ENV DiscordToken_mbox=${DiscordToken_mbox} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \

# Update apt-get and install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /app
COPY . .

# Install requirements from requirements.txt
RUN pip install -r requirements.txt

# Run the application
CMD . .venv/bin/activate && python3 main.py
