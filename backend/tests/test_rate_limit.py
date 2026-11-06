def _post(client, **kw):
    return client.post("/message", json={"ciphertext": "abc"}, **kw)


def test_post_limit_10_per_minute(client):
    for i in range(10):
        assert _post(client).status_code == 200, f"request {i+1} fail hui"
    assert _post(client).status_code == 429


def test_get_limit_15_per_minute(client):
    for _ in range(15):
        assert client.get("/message/fake-id").status_code == 404
    assert client.get("/message/fake-id").status_code == 429


def test_post_and_get_limits_are_separate(client):
    for _ in range(11):
        _post(client)  
    assert client.get("/message/fake-id").status_code == 404  


def test_spoofed_forwarded_for_does_not_bypass_limit(client):
    
    codes = [
        _post(client, headers={"X-Forwarded-For": f"1.2.3.{i}"}).status_code
        for i in range(11)
    ]
    assert codes[-1] == 429


def test_blocked_request_does_not_create_message(client, fake_redis):
    for _ in range(15):
        _post(client)
    assert len(fake_redis.keys("msg:*")) == 10



