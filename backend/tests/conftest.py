import fakeredis
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import message_service


@pytest.fixture
def client(monkeypatch):
    # asli Redis ki jagah nakli (memory wala) Redis, taaki tests kuch bigaad na sakein
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(message_service, "redis_client", fake)
    return TestClient(app)

