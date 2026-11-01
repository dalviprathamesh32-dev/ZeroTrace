from fastapi import FastAPI

from app.routes import message

app = FastAPI()

app.include_router(message.router)

@app.get("/")
def Health_check ():
    return {"message" : "all okk"}

