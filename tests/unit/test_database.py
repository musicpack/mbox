from src.element.database import Record


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
