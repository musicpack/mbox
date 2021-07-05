from typing import List

from src.element.database import DynamoDB, Record


def test_record():
    sample_kwargs = {
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


def test_store_record():
    db = DynamoDB(758005098042622194)

    # Adding guild item to database first time bot joins server
    record = Record(guild_id=287654321098765432)
    put_response: dict = db.store_record(record)
    print(f"Printing response from Dynamo: {put_response}")


def test_get_record():
    db = DynamoDB(758005098042622194)

    # record = Record(guild_id=987654321098765432)
    record_responce: Record = db.get_record(987654321098765432)

    assert record_responce.guild_id == 987654321098765432
    assert record_responce.volume == 50
    assert record_responce.admin_channel_id == None

    print(record_responce)


def test_get_all_records():
    db = DynamoDB(758005098042622194)

    record_responce: List[Record] = db.get_all_records()

    assert len(record_responce) == 2

    print(record_responce)
