import redis
import secrets
from fastapi import FastAPI , HTTPException
from pydantic import BaseModel

class Message(BaseModel) :
    ciphertext : str

r = redis.Redis (host="localhost" , port=6379 , decode_responses=True)

app = FastAPI()

@app.get("/health")
def health_check():
    return {"message": "all okk"}

@app.post("/message")
def send_text(msg : Message):
    msg_id = secrets.token_urlsafe(16)
    r.set (f"msg:{msg_id}", msg.ciphertext, ex=3600)
    return {"id" : msg_id }

@app.get("/message/{msg_id}")
def get_text(msg_id : str):
    key = f"msg:{msg_id}"
    pipe = r.pipeline()
    pipe.get(key)
    pipe.delete(key)
    data, _ = pipe.execute()
    if data is None:
        raise HTTPException(status_code=404 , detail="not found or viewed early")
    return {"ciphertext" : data}


