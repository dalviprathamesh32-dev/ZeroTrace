from pydantic import BaseModel , Field

from app.core.config import settings


class MessageCreate (BaseModel):
    ciphertext : str = Field(min_length=1 , max_length=settings.max_msg_length)
    expiry_time : int = settings.msg_ttl_seconds

