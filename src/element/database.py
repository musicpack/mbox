from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Dict, List

import boto3
from boto3.dynamodb.conditions import Key


@dataclass
class Record:
    """Holds all attributes for one guild in the database.

    Similar to the deprecated profile object.
    """

    application_id: int = None
    guild_id: int = None
    command_channel_id: int = None
    admin_channel_id: int = None
    volume: int = 50
    webhook_message_url: str = None
    webhook_message_id: str = None


class Database(ABC):
    """An Abstract Base Classes (ABCs) that details functions needed in a database implementation"""

    @abstractmethod
    def is_command_channel(self, channel_id: int) -> bool:
        """Checks if a command_channel exists in the database.

        If a channel_id record provided exists in the database,
        it is assumed that a command_channel is registered and functional.

        Args:
            channel_id (int): discord.TextChannel.id

        Returns:
            bool: True/False if entry exists/not exist
        """
        pass

    @abstractmethod
    def get_command_channel(self, guild_id: int) -> int:
        """Gets the command_channel_id based on guild_id.

        Args:
            guild_id (int): discord.guild.id integer

        Returns:
            int: command channel id in the database
        """
        pass


class DynamoDB(Database):
    def __init__(self, application_id: int):
        dynamodb = boto3.resource(
            service_name="dynamodb", region_name="us-east-2"
        )
        self.table = dynamodb.Table("music-box-db")
        self.application_id: int = application_id
        self.record_cache: Dict[int, Record] = {}  # dict{guild_id, record}
        self.guild_items = []

    def cache_record(self, record: Record) -> None:
        """Stores the record in the internal cache.

        Updates Record if different then what is stored.

        Args:
            record (Record): Latest, up to date Record object
        """
        self.record_cache[record.guild_id] = record

    def parse_record_response(self, guild_id: int, response: dict) -> Record:
        """Parses a specific responce when called with a composite key (primary + sort)

        Args:
            guild_id (int): guild_id that was called
            response (dict): responce from aws

        Returns:
            Record: resulting record object
        """
        kwargs = {key: value for key, value in response.items()}
        return Record(**kwargs)

    def store_record(self, record: Record) -> dict:
        """Stores the record in the remote database

        Args:
            record (Record): record to store

        Returns:
            dict: responce from AWS
        """
        self.cache_record(record)
        record_dict = asdict(record)
        record_dict["application_id"] = self.application_id
        response = self.table.put_item(Item=record_dict)
        return response

    def get_record(self, guild_id: int) -> Record:
        """Gets a record in the database by using the sort key.

        If the record does not exist in cache, call the db and save that record to the internal cache.

        Args:
            guild_id (int): sort key

        Returns:
            Record: Resulting data from database.
        """
        if guild_id in self.record_cache:
            return self.record_cache[guild_id]
        else:
            response = self.table.get_item(
                Key={
                    "application_id": self.application_id,
                    "guild_id": guild_id,
                }
            )
            record = self.parse_record_response(
                guild_id=guild_id, response=response["Item"]
            )
            self.cache_record(record)
            return record

    def get_all_records(self) -> List[Record]:
        """Grabs all entries based on primary key.

        Returns:
            List[Record]: All records in the database based on application_id
        """
        record_list = []
        response = self.table.query(
            KeyConditionExpression=Key("application_id").eq(
                self.application_id
            )
        )
        for raw_guild_response in response["Items"]:
            record = self.parse_record_response(
                guild_id=raw_guild_response["guild_id"],
                response=raw_guild_response,
            )

            self.cache_record(record)
            record_list.append(record)

        return record_list

    def is_command_channel(self, channel_id: int) -> bool:
        """Checks if a command_channel exists in the database.

        If a channel_id record provided exists in the database,
        it is assumed that a command_channel is registered and functional.

        Args:
            channel_id (int): discord.TextChannel.id

        Returns:
            bool: True/False if entry exists/not exist
        """
        # Check the cache before calling dynamodb
        for record in self.record_cache.values():
            if record.command_channel_id == channel_id:
                return True

        # Call the db and find the channel_id from all the records
        for record in self.get_all_records():
            if record.command_channel_id == channel_id:
                return True

        return False

    def get_command_channel(self, guild_id: int) -> int:
        """Gets the command_channel_id based on guild_id.

        Args:
            guild_id (int): discord.guild.id integer

        Returns:
            int: command channel id in the database
        """
        record = self.get_record(guild_id=guild_id)
        return record.command_channel_id
