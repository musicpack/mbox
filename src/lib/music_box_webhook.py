import logging
from typing import List
import aiohttp
from botocore.exceptions import ClientError
import discord
from discord import AsyncWebhookAdapter
from discord_slash import SlashContext
import boto3


class MusicBoxWebhook:
    def __init__(self):
        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table('music-box')
        self.avatar_url = "https://cdn.discordapp.com/avatars/758005098042622194/34205017807cce1c9f7bfcb2f4e3bcd7.webp?size=256"

    async def send_message(self, ctx: SlashContext):
        guild: dict = self.get_guild_item(ctx.guild_id)

        # If webhook does not exist for url, create webhook, send webhook message, and save webhook message id in database.
        if 'webhookUrl' not in guild.keys():
            webhook = await self.generate_webhook(ctx.guild)
            webhook_message: discord.WebhookMessage = await webhook.send(content="Hello", wait=True, avatar_url=self.avatar_url)
            self.save_message_id(webhook.guild_id, webhook_message.id)

        # Otherwise, get webhook url from database, create webhook using webhook url, send message using generated webhook,
        # update most recent webhook message id in database.
        else:
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(
                    guild['webhookUrl'], adapter=AsyncWebhookAdapter(session))
                webhook_message: discord.WebhookMessage = await webhook.send(content="Hello", wait=True, avatar_url=self.avatar_url)
                self.update_message_id(ctx.guild_id, webhook_message.id)

    async def edit_embed_message(self, guild_id: int):
        # Get message id and webhook url
        guild: dict = self.get_guild_item(guild_id)
        message_id: int = guild['messageId']
        webhook_url: str = guild['webhookUrl']

        # Create test embeds
        first_embed = discord.Embed(
            title="This first embed is coming from webhook")
        second_embed = discord.Embed(
            title="This second embed is coming from webhook")

        # Edit webhook message
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(
                webhook_url, adapter=AsyncWebhookAdapter(session))
            await webhook.edit_message(message_id=message_id, content=None, embeds=[first_embed, second_embed])

    async def generate_webhook(self, guild: discord.Guild) -> discord.Webhook:
        music_channel = self.get_music_channel(guild)

        # Create webhook
        webhook: discord.Webhook = await music_channel.create_webhook(name="Music Box")

        # Save webhook.url in database for associated guild id
        self.table.put_item(Item={
            'guildId': str(webhook.guild_id),
            'webhookUrl': webhook.url
        })
        return webhook

    def get_music_channel(self, guild: discord.Guild):
        # Get list of all text channels within guild
        text_channels: List[discord.TextChannel] = guild.text_channels

        #  Loop through all text channel list to find text channel labeled as "music-box"
        # TODO: Check if there are two text channels with 'music-box' name
        for text_channel in text_channels:
            if text_channel.name == "music-box":
                return text_channel

        logging.error(
            f"Cannot find music-box channel for guild id ({guild.id}")

    def get_guild_item(self, guild_id: int):
        try:
            response = self.table.get_item(Key={
                'guildId': str(guild_id)
            })
            return response['Item']
        except ClientError:
            logging.error(f"Cannot find guild id ({guild_id}) in database.")

    def save_message_id(self, guild_id: int, message_id: int) -> None:
        try:
            self.table.update_item(
                Key={'guildId': str(guild_id)},
                UpdateExpression="ADD messageId :message_id",
                ExpressionAttributeValues={":message_id": message_id})
        except ClientError:
            logging.error(
                f"An error occurred trying to save message_id ({message_id}) for the associated guild id ({guild_id}).")

    def update_message_id(self, guild_id: int, message_id: int) -> None:
        try:
            self.table.update_item(
                Key={'guildId': str(guild_id)},
                UpdateExpression="SET messageId = :message_id",
                ExpressionAttributeValues={":message_id": message_id})
        except ClientError:
            logging.error(
                f"An error occurred trying to update message_id ({message_id}) for the associated guild id ({guild_id}).")


music_box_webhook = MusicBoxWebhook()
