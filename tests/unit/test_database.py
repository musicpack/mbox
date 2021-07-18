from typing import List

import boto3
import pytest
from moto import mock_dynamodb2

from src.element.database import DynamoDB, Record

sample_record_list: List[Record] = [
    Record(
        application_id=987654321098765432,
        guild_id=111111111111111111,
        command_channel_id=111111111111111111,
        admin_channel_id=111111111111111111,
        webhook_message_id=111111111111111111,
        webhook_message_url="SAMPLE_RECORD_ONE-sample_record_one-SAMPLE_RECORD_ONE-sample_record_one-SAMPLE_RECORD_ONE-sample_record_one-SAMPLE_RECORD_ONE",
        volume=100,
    ),
    Record(
        application_id=987654321098765432,
        guild_id=222222222222222222,
        command_channel_id=222222222222222222,
        admin_channel_id=222222222222222222,
        webhook_message_id=222222222222222222,
        webhook_message_url="SAMPLE_RECORD_TWO-sample_record_two-SAMPLE_RECORD_TWO-sample_record_two-SAMPLE_RECORD_TWO-sample_record_two-SAMPLE_RECORD_TWO",
        volume=100,
    ),
]


@pytest.fixture
def dynamodb_table():
    with mock_dynamodb2():
        dynamodb_client = boto3.client("dynamodb", region_name="us-east-2")
        dynamodb_client.create_table(
            TableName="music-box-db",
            KeySchema=[
                {"AttributeName": "application_id", "KeyType": "HASH"},
                {"AttributeName": "guild_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "application_id", "AttributeType": "S"},
                {"AttributeName": "guild_id", "AttributeType": "S"},
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 10,
                "WriteCapacityUnits": 10,
            },
        )

        table = boto3.resource("dynamodb", region_name="us-east-2").Table(
            "music-box-db"
        )

        table.put_item(Item=sample_record_list[0].__dict__)
        table.put_item(Item=sample_record_list[1].__dict__)

        yield table


@pytest.fixture
def guild_table():
    guild_table: DynamoDB = DynamoDB(987654321098765432)
    yield guild_table


def test_store_record(dynamodb_table, guild_table):
    sample_record: Record = Record(
        application_id=987654321098765432,
        guild_id=333333333333333333,
        command_channel_id=333333333333333333,
        admin_channel_id=333333333333333333,
        webhook_message_id=333333333333333333,
        webhook_message_url="SAMPLE_RECORD_THREE-sample_record_three-SAMPLE_RECORD_THREE-sample_record_three-SAMPLE_RECORD_THREE-sample_record_three-SAMPLE_RECORD_THREE",
        volume=100,
    )

    guild_table.store_record(sample_record)

    response = dynamodb_table.get_item(
        Key={
            "application_id": sample_record.application_id,
            "guild_id": sample_record.guild_id,
        }
    )

    assert response["Item"] == sample_record.__dict__


def test_get_record(guild_table: DynamoDB):
    record = guild_table.get_record(sample_record_list[0].guild_id)

    assert record == sample_record_list[0]


def test_get_all_records(guild_table: DynamoDB):
    records = guild_table.get_all_records()

    assert records == sample_record_list
