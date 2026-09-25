Name: Sobar Danil 
Group: PO 25-Z 
Date: 25.09.26

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_author_min_length_rejected():
    r = client.post("/users", json={"author": "a", "password": "longpassword"})
    assert r.status_code == 422


def test_author_max_length_rejected():
    r = client.post("/users", json={"author": "a" * 33, "password": "longpassword"})
    assert r.status_code == 422


def test_create_user_201_and_no_password_in_response():
    r = client.post("/users", json={"author": "alice", "password": "supersecret"})
    assert r.status_code == 201
    body = r.json()
    assert "password" not in body
    assert body["author"] == "alice"


def test_blank_text_returns_422():
    r = client.post(
        "/messages",
        json={"author": "alice", "text": "     ", "room_id": 1},
    )
    assert r.status_code == 422


def test_text_is_stored_trimmed():
    r = client.post(
        "/messages",
        json={"author": "alice", "text": "  hello there  ", "room_id": 1},
    )
    assert r.status_code == 201
    assert r.json()["text"] == "hello there"


def test_text_max_length():
    r = client.post(
        "/messages",
        json={"author": "alice", "text": "x" * 501, "room_id": 1},
    )
    assert r.status_code == 422


def test_room_id_below_one_rejected():
    r = client.post(
        "/messages",
        json={"author": "alice", "text": "hi", "room_id": 0},
    )
    assert r.status_code == 422


def test_room_id_equal_one_accepted():
    r = client.post(
        "/messages",
        json={"author": "alice", "text": "hi", "room_id": 1},
    )
    assert r.status_code == 201
