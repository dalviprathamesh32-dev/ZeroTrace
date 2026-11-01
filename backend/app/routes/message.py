from fastapi import APIRouter , HTTPException

from app.services import message_service
from app.schemas.message import MessageCreate


router = APIRouter(prefix="/message" , tags=["Message"])

@router.post("/")
def send_msg (msg : MessageCreate):
    msg_id = message_service.send_text(msg.ciphertext)
    return {"msg_id" : msg_id}

@router.get("/{msg_id}")
def get_msg (msg_id : str):
    msg = message_service.get_text(msg_id)
    if msg is None:
        raise HTTPException(status_code=404 , detail="Not found or viewed early or get burned")
    return {"ciphertext" : msg}




