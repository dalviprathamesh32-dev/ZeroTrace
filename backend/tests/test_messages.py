def test_health(client):
    assert client.get("/health").status_code == 200


def test_create_returns_id(client):
    res = client.post("/message", json={"ciphertext": "abc"})
    assert res.status_code == 200
    assert "id" in res.json()


def test_view_once(client):
    msg_id = client.post("/message", json={"ciphertext": "abc"}).json()["id"]

    first = client.get(f"/message/{msg_id}")
    assert first.status_code == 200
    assert first.json()["ciphertext"] == "abc"

    second = client.get(f"/message/{msg_id}")
    assert second.status_code == 404


def test_unknown_id_is_404(client):
    assert client.get("/message/doesnotexist").status_code == 404


def test_oversize_rejected(client):
    res = client.post("/message", json={"ciphertext": "a" * 20001})
    assert res.status_code == 422


def test_empty_rejected(client):
    res = client.post("/message", json={"ciphertext": ""})
    assert res.status_code == 422



