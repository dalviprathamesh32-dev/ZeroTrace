from fastapi import FastAPI, Request

from app.core.config import settings


def set_CSP(app: FastAPI):
    @app.middleware("http")
    async def csp_headers(request: Request, call_next):
        response = await call_next(request)

        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "object-src 'none'"
        )

        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"

        response.headers["Referrer-Policy"] = "no-referrer"

        if request.url.path.startswith("/message"):
            response.headers["Cache-Control"] = "no-store"

        if settings.app_env == "production":
            response.headers["Strict-Transport-Security"] = "max-age=86400"

        return response



