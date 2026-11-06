import re
from pathlib import Path

import pytest

from app.core.config import settings

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


def test_csp_blocks_everything_outside_self(client):
    csp = client.get("/health").headers["content-security-policy"]
    for part in ("default-src 'self'", "script-src 'self'", "frame-ancestors 'none'",
                 "object-src 'none'", "base-uri 'self'"):
        assert part in csp


def test_csp_has_no_dangerous_values(client):
    csp = client.get("/health").headers["content-security-policy"]
    assert "unsafe-inline" not in csp
    assert "unsafe-eval" not in csp
    assert "*" not in csp


@pytest.mark.parametrize("path", ["/health", "/nope-404"])
def test_headers_present_on_every_response(client, path):
    h = client.get(path).headers
    assert h["x-frame-options"] == "DENY"
    assert h["x-content-type-options"] == "nosniff"
    assert h["referrer-policy"] == "no-referrer"
    assert "content-security-policy" in h


def test_headers_present_even_on_429(client):
    for _ in range(16):
        r = client.get("/message/abc")
    assert r.status_code == 429
    assert "content-security-policy" in r.headers


def test_api_responses_are_not_cached(client):
    r = client.post("/message", json={"ciphertext": "abc"})
    assert r.headers["cache-control"] == "no-store"
    r = client.get("/message/whatever")
    assert r.headers["cache-control"] == "no-store"


def test_hsts_only_in_production(client, monkeypatch):
    monkeypatch.setattr(settings, "app_env", "development")
    assert "strict-transport-security" not in client.get("/health").headers
    monkeypatch.setattr(settings, "app_env", "production")
    assert "max-age" in client.get("/health").headers["strict-transport-security"]

@pytest.mark.parametrize("name", ["index.html", "view.html"])
def test_frontend_has_no_inline_code(name):
    html = (FRONTEND / name).read_text(encoding="utf-8")
    assert not re.search(r"<script(?![^>]*\bsrc=)[^>]*>", html), "inline <script> mila"
    assert "<style" not in html, "inline <style> mila"
    assert not re.search(r'\sstyle\s*=', html), "style=... attribute mila"
    assert not re.search(r'\son[a-z]+\s*=', html), "onclick= jaisa inline handler mila"
    assert not re.search(r'(src|href)=["\']https?://', html), "external resource mila, CSP block karega"

