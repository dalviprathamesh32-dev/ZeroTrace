from fastapi import FastAPI
from app.core.cors import setup_cors
from app.routes import message

app = FastAPI()

setup_cors(app)

app.include_router(message.router)

@app.get("/health")
def Health_check ():
    return {"message" : "all okk"}

