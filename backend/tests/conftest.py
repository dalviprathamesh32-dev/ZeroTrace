import os

os.environ["RATE_LIMITER_REDIS_URL"] = "memory://"

import fakeredis
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import message_service
from app.core.rate_limiter import limiter


@pytest.fixture
def fake_redis(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(message_service, "redis_client", fake)
    return fake


@pytest.fixture
def client(fake_redis):
    limiter.reset()
    return TestClient(app)

