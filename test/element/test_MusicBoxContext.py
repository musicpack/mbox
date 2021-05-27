import pytest
from src.element.MusicBoxContext import MusicBoxContext


def test_context_general_message_version():
    class FakeMessage(NotImplementedError):
        pass
    a = FakeMessage()
    a._state = NotImplementedError
    assert MusicBoxContext(prefix='',profile=None,name='',slash_context=None,message=a,args=None,kwargs=None)

def test_context_slashcommand_version():
    class FakeSlashContext(NotImplementedError):
        pass
    ctx = MusicBoxContext(prefix='/',profile=None,name='c',slash_context=FakeSlashContext,message=None,args=None,kwargs=None)
    assert ctx.message == None

def test_verify_context():
    with pytest.raises(Exception) as excinfo:
        MusicBoxContext(prefix='/',profile=None,name='c',slash_context=None,message=None,args=None,kwargs=None)

    assert "slash_context and prefix values do not line up" in str(excinfo.value)
