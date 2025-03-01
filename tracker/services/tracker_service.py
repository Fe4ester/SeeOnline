from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import UserStatusOnline, UserStatusOffline


# Запросит номер телефона, и код в терминале
def default_auth(api_id, api_hash):
    try:
        with TelegramClient(StringSession(), api_id, api_hash) as client:
            return client.session.save()

    except Exception as e:
        print(f"Ошибка авторизации: {e}")
        return


def check_online(username, api_hash, api_id, session_string):
    with TelegramClient(StringSession(session_string), api_id, api_hash) as client:
        user = client.get_entity(username)
        if isinstance(user.status, UserStatusOnline):
            return True
        elif isinstance(user.status, UserStatusOffline):
            return False
        else:
            return
