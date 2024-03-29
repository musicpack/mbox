import os
from typing import List

import boto3
import pytest
from moto import mock_dynamodb2

from src.element.database import DynamoDB, Record


@pytest.fixture(scope="function")
def sample_record_list():
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
    yield sample_record_list


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope="function")
def dynamodb_table(aws_credentials, sample_record_list):
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


@pytest.fixture(scope="function")
def guild_table():
    guild_table: DynamoDB = DynamoDB(987654321098765432)
    yield guild_table
