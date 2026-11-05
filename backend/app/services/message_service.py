import secrets

from app.db import redis_client
from app.core.config import settings



def _key (msg_id : str) -> str:
    return f"msg:{msg_id}"

def send_text (ciphertext : str , expiry_time : int) -> str:
    msg_id = secrets.token_urlsafe(16)
    redis_client.set(_key(msg_id), ciphertext , ex=expiry_time)
    return msg_id

def get_text (msg_id : str) -> str | None :
    pipe = redis_client.pipeline()
    pipe.get(_key(msg_id))
    pipe.delete(_key(msg_id))
    data , trash = pipe.execute()
    if data is None:
        return None
    return data



