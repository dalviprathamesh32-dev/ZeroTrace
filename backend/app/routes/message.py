from fastapi import APIRouter , HTTPException , Request

from app.services import message_service
from app.schemas.message import MessageCreate

from app.core.rate_limiter import limiter


router = APIRouter(prefix="/message" , tags=["Message"])

@router.post("")
@limiter.limit("10/minute")
def send_msg (request : Request , msg : MessageCreate):
    msg_id = message_service.send_text(msg.ciphertext , msg.expiry_time)
    return {"id" : msg_id}

@router.get("/{msg_id}")
@limiter.limit("15/minute")
def get_msg (request : Request , msg_id : str):
    msg = message_service.get_text(msg_id)
    if msg is None:
        raise HTTPException(status_code=404 , detail="Not found or viewed early or get burned")
    return {"ciphertext" : msg}




