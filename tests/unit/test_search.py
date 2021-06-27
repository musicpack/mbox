from src.search import youtube, youtube_music


def test_youtube():
    result = youtube("dQw4w9WgXcQ")
    assert result == "dQw4w9WgXcQ"


def test_youtube_music():
    result = youtube_music("dQw4w9WgXcQ")
    assert result == "dQw4w9WgXcQ" or result == "i5VeMbagIaU"
