# syntax=docker/dockerfile:1

ARG DiscordToken_mbox
FROM python:3.7.10-slim-buster
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /app
COPY requirements_locked.txt requirements_locked.txt
RUN pip3 install -r requirements_locked.txt
COPY . .
CMD [ "python3", "./main.py"]