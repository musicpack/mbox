from dataclasses import asdict
from typing import List

from src.element.database import DynamoDB, Record


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
    record_dict = asdict(
        sample_record,
        dict_factory=lambda data: dict(x for x in data if x[1] is not None),
    )
    assert response["Item"] == record_dict


def test_get_record(
    dynamodb_table, guild_table: DynamoDB, sample_record_list: List[Record]
):
    record = guild_table.get_record(sample_record_list[0].guild_id)
    assert record == sample_record_list[0]


def test_get_all_records(
    dynamodb_table, guild_table: DynamoDB, sample_record_list: List[Record]
):
    records = guild_table.get_all_records()
    assert records == sample_record_list
