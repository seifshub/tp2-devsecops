import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(db_path=str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_security_headers(client):
    res = client.get("/health")
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in res.headers["Content-Security-Policy"]
    assert res.headers["Cache-Control"] == "no-store"


def test_list_notes_empty(client):
    res = client.get("/notes")
    assert res.status_code == 200
    assert res.get_json() == []


def test_create_and_get_note(client):
    res = client.post("/notes", json={"title": "Hello", "content": "World"})
    assert res.status_code == 201
    note_id = res.get_json()["id"]

    res = client.get(f"/notes/{note_id}")
    assert res.status_code == 200
    assert res.get_json() == {"id": note_id, "title": "Hello", "content": "World"}


@pytest.mark.parametrize(
    "payload",
    [{}, {"title": "", "content": "x"}, {"title": "ok", "content": 42}],
)
def test_create_note_rejects_invalid_input(client, payload):
    res = client.post("/notes", json=payload)
    assert res.status_code == 400


def test_get_missing_note_returns_404(client):
    assert client.get("/notes/999").status_code == 404


def test_search_notes(client):
    client.post("/notes", json={"title": "groceries", "content": "milk"})
    client.post("/notes", json={"title": "homework", "content": "devsecops"})

    res = client.get("/notes/search", query_string={"q": "home"})
    assert [n["title"] for n in res.get_json()] == ["homework"]


def test_lookup_resolves_localhost(client):
    res = client.get("/lookup", query_string={"host": "localhost"})
    assert res.status_code == 200
    assert "localhost" in res.get_json()["output"]


def test_search_treats_sql_as_plain_text(client):
    client.post("/notes", json={"title": "secret", "content": "x"})

    res = client.get("/notes/search", query_string={"q": "' OR '1'='1"})
    assert res.status_code == 200
    assert res.get_json() == []
