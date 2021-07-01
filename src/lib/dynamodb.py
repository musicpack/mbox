import boto3
import logging
from botocore.exceptions import ClientError


class Dynamodb:
    def __init__(self):
        dynamodb = boto3.resource(
            service_name='dynamodb', region_name="us-east-2")
        self.table = dynamodb.Table('music-box-db')

    def store_guild_item(self, application_id: int, guild_id: int) -> dict:
        """Takes in a application id as the primary key and creates an object for the guild in dynamodb

        Args:
            application_id (int): The id of the bot/application 
            guild_id (int): The id of the guild/server that the bot is in

        Returns:
            dict: The response object indicating the status of the request
        """
        # response = self.table.put_item(
        #     Item={
        #         'guild_channel+application_id': str(guild_id) + "_" + application_id,
        #         'command_channel_id': "",
        #         'admin_channel_id': "",
        #         'webhook_message_url': ""
        #     }
        # )

        response = self.table.put_item(
            Item={
                'application_id': application_id,
                'guild_id': guild_id,
                'volume_level': 50
            }
        )
        logging.info("Saved information to dynamo table")
        return response

    def retrieve_guild_item(self, application_id: int) -> dict:
        """Returns the DynamoDb record based on the application id provided

        Args:
            guild_id (int): The id of the guild/server that the bot is in

        Returns:
            dict: The record object containing the data associated with a application id
        """
        try:
            response = self.table.get_item(
                Key={
                    'application_id': application_id
                }
            )
            logging.info("retrieved information from dynamo table")

        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            return response['Item']

    def delete_guild_item(self, application_id: int) -> dict:
        """Deletes the DynamoDb record based on the application id provided

        Args:
            application_id (int): The id of the application/bot

        Returns:
            dict: The response object indicating the status of the request as well as the info about the item deleted
        """
        try:
            response = self.table.delete_item(
                Key={
                    'application_id': application_id
                }
            )

        except ClientError as e:
            raise e
        else:
            return response
