from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import UserStatusOnline, UserStatusOffline
from telethon.errors import UsernameNotOccupiedError


def check_online(username, api_hash, api_id, session_string):
    try:
        with TelegramClient(StringSession(session_string), api_id, api_hash) as client:
            user = client.get_entity(username)
            if isinstance(user.status, UserStatusOnline):
                return True
            elif isinstance(user.status, UserStatusOffline):
                return False
            else:
                return None
    except UsernameNotOccupiedError:
        return None
    except Exception as e:
        return None


def auth(api_id, api_hash):
    try:
        with TelegramClient(StringSession(), api_id, api_hash) as client:
            return client.session.save()
    except:
        return None
