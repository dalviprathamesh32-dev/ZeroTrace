import pytest
from app.core.config import settings
from fastapi.testclient import TestClient


def _create(client, text="hello"):
    return client.post("/message", json={"ciphertext": text}).json()["id"]


def test_message_burns_after_first_read(client):
    msg_id = _create(client, "secret-ciphertext")
    first = client.get(f"/message/{msg_id}")
    assert first.status_code == 200
    assert first.json()["ciphertext"] == "secret-ciphertext"
    assert client.get(f"/message/{msg_id}").status_code == 404


def test_unicode_roundtrip(client):
    text = "नमस्ते-🔐-abc"
    assert client.get(f"/message/{_create(client, text)}").json()["ciphertext"] == text


def test_ids_are_long_and_unique(client, monkeypatch):
    ids = set()
    for _ in range(9):
        ids.add(_create(client))
    assert len(ids) == 9
    assert all(len(i) >= 22 for i in ids)  # 128-bit token


def test_oversized_ciphertext_rejected(client):
    r = client.post("/message", json={"ciphertext": "a" * 20001})
    assert r.status_code == 422


@pytest.mark.parametrize("body", [
    {},
    {"ciphertext": ""},
    {"ciphertext": None},
    {"ciphertext": ["a"]},
    {"ciphertext": {"a": 1}},
    {"ciphertext": 123},
])
def test_bad_body_rejected(client, body):
    assert client.post("/message", json=body).status_code == 422


def test_invalid_json_rejected(client):
    r = client.post("/message", content="{not json", headers={"Content-Type": "application/json"})
    assert r.status_code == 422


@pytest.mark.parametrize("evil_id", [
    "../../etc/passwd",
    "' OR 1=1 --",
    "*",
    "msg:*",
    "a" * 5000,
    "%00",
    "<script>alert(1)</script>",
])
def test_weird_ids_never_crash_or_leak(client, evil_id):
    r = client.get(f"/message/{evil_id}")
    assert r.status_code in (404, 429, 422)  
    assert "ciphertext" not in r.text


def test_cannot_read_other_keys_with_glob(client):
    _create(client, "private")
    assert client.get("/message/*").status_code == 404


def test_evil_origin_not_allowed(client):
    r = client.get("/health", headers={"Origin": "https://evil.example"})
    allowed = r.headers.get("access-control-allow-origin")
    assert allowed not in ("*", "https://evil.example")


def test_docs_hidden_in_production(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")
    from importlib import reload
    import app.main as m
    reload(m)
    c = TestClient(m.app)
    assert c.get("/docs").status_code == 404




