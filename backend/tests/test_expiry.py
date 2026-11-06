import os
import time

import pytest


def _create(client, **extra):
    return client.post("/message", json={"ciphertext": "abc", **extra})


@pytest.mark.parametrize("seconds", [60, 300, 3600, 86400])
def test_ttl_is_set_in_redis(client, fake_redis, seconds):
    r = _create(client, expiry_time=seconds)
    assert r.status_code == 200
    ttl = fake_redis.ttl(f"msg:{r.json()['id']}")
    assert seconds - 3 <= ttl <= seconds


def test_default_ttl_when_not_sent(client, fake_redis):
    r = _create(client)
    assert 3590 <= fake_redis.ttl(f"msg:{r.json()['id']}") <= 3600



@pytest.mark.parametrize("bad", [0, -1, 59, 86401, 999999, 10**12, "abc", 1.5, None, [], {}])
def test_bad_expiry_is_rejected(client, bad):
    assert _create(client, expiry_time=bad).status_code == 422


def test_bad_expiry_stores_nothing(client, fake_redis):
    _create(client, expiry_time=999999)
    assert fake_redis.keys("*") == []


@pytest.mark.skipif(not os.getenv("RUN_SLOW"), reason="61 second leta hai, RUN_SLOW=1 se chala")
def test_message_really_expires_after_60s(client):
    msg_id = _create(client, expiry_time=60).json()["id"]
    time.sleep(61)
    assert client.get(f"/message/{msg_id}").status_code == 404



