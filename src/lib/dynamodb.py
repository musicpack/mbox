import boto3
import logging
from botocore.exceptions import ClientError


class Dynamodb:
    def __init__(self):
        dynamodb = boto3.resource(
            service_name='dynamodb', region_name="us-east-2")
        self.table = dynamodb.Table('music-box')

    def store_guild_id_info(self, guild_id: int) -> dict:
        """Takes in a guild id as the primary key and creates an object for the guild in dynamodb

        Args:
            guild_id (int): The id of the guild/server that the bot is in

        Returns:
            dict: The response object indicating the status of the request
        """
        response = self.table.put_item(
            Item={
                'guildId': str(guild_id),
                'messageId': guild_id,
                'webhookUrl': ""
            }
        )
        logging.info("Saved guild_id to dynamo table")
        return response

    def retrieve_guild_id_info(self, guild_id: int) -> dict:
        """Returns the DynamoDb record based on the guild id provided

        Args:
            guild_id (int): The id of the guild/server that the bot is in

        Returns:
            dict: The record object containing the data associated with a guild id
        """
        try:
            response = self.table.get_item(
                Key={
                    'guildId': str(guild_id)
                }
            )
            logging.info("retrieved guild_id from dynamo table")

        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            return response['Item']

    def delete_guild_id_info(self, guild_id: int) -> dict:
        """Deletes the DynamoDb record based on the guild id provided

        Args:
            guild_id (int): The id of the guild/server that the bot is in

        Returns:
            dict: The response object indicating the status of the request as well as the info about the item deleted
        """
        try:
            response = self.table.delete_item(
                Key={
                    'guildId': str(guild_id)
                }
            )

        except ClientError as e:
            raise e
        else:
            return response
