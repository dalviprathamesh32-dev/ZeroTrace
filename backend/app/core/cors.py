from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from fastapi import FastAPI

def setup_cors(app : FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins= settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET","POST"],
        allow_headers=["Content-Type"]
    )

