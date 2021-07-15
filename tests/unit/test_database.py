from typing import List

from src.element.database import DynamoDB, Record


def test_record():
    sample_kwargs = {
        "application_id": 987654321098765432,
        "guild_id": 987654321098765432,
        "command_channel_id": 987654321098765432,
        "admin_channel_id": 987654321098765432,
        "webhook_message_id": 987654321098765432,
        "webhook_message_url": "https://discord.com/api/webhooks/987654321098765432/ZZZZZZZZZZZZZZZ_Z-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA-BBBBBBBBBBB_CC-DD",
        "volume": 100,
    }

    record = Record(**sample_kwargs)
    record2 = Record(**sample_kwargs)

    assert record.guild_id == sample_kwargs["guild_id"]
    assert record.command_channel_id == sample_kwargs["command_channel_id"]
    assert record.admin_channel_id == sample_kwargs["admin_channel_id"]
    assert record.webhook_message_url == sample_kwargs["webhook_message_url"]
    assert record.volume == sample_kwargs["volume"]
    assert record == record2

    record.volume = 0
    assert record != record2

    record = Record()
    assert record.volume == 50


def sample_record_one():
    return Record(
        application_id=987654321098765432,
        guild_id=111111111111111111,
        command_channel_id=111111111111111111,
        admin_channel_id=111111111111111111,
        webhook_message_id=111111111111111111,
        webhook_message_url="SAMPLE_RECORD_ONE-sample_record_one-SAMPLE_RECORD_ONE-sample_record_one-SAMPLE_RECORD_ONE-sample_record_one-SAMPLE_RECORD_ONE",
        volume=100,
    )


def sample_record_two():
    return Record(
        application_id=987654321098765432,
        guild_id=222222222222222222,
        command_channel_id=222222222222222222,
        admin_channel_id=222222222222222222,
        webhook_message_id=222222222222222222,
        webhook_message_url="SAMPLE_RECORD_TWO-sample_record_two-SAMPLE_RECORD_TWO-sample_record_two-SAMPLE_RECORD_TWO-sample_record_two-SAMPLE_RECORD_TWO",
        volume=100,
    )


def test_store_record():
    db = DynamoDB(987654321098765432)

    record_one = sample_record_one()
    put_response: dict = db.store_record(record_one)

    assert put_response["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_get_record():
    db = DynamoDB(987654321098765432)

    record_two = sample_record_two()
    put_response: dict = db.store_record(record_two)
    assert put_response["ResponseMetadata"]["HTTPStatusCode"] == 200

    record_responce: Record = db.get_record(record_two.guild_id)

    assert record_responce == record_two


def test_get_all_records():
    db = DynamoDB(987654321098765432)

    record_one = sample_record_one()
    db.store_record(record_one)
    record_two = sample_record_two()
    db.store_record(record_two)

    record_responce: List[Record] = db.get_all_records()

    assert record_one in record_responce
    assert record_two in record_responce
