from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.cors import setup_cors
from app.routes import message

app = FastAPI()
setup_cors(app)
app.include_router(message.router)


@app.get("/health")
def health_check():
    return {"message": "all ok"}


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

