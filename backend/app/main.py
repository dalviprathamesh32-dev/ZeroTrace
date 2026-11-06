from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.cors import setup_cors
from app.routes import message

from app.core.rate_limiter import rate_limiter
from app.core.CSP import set_CSP

from app.core.config import settings

is_prod = settings.app_env == "production"
app = FastAPI(
    docs_url=None if is_prod else "/docs",
    redoc_url=None,
    openapi_url=None if is_prod else "/openapi.json",
)

# cors config
setup_cors(app)

# routes config -- message
app.include_router(message.router)

# rate-limiter config
rate_limiter(app)

# Adding Content security policy
set_CSP(app)


@app.get("/health")
def health_check():
    return {"message": "all ok"}


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

