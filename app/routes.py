from flask import Blueprint, abort, jsonify, request

from .db import get_db

bp = Blueprint("notes", __name__)


def note_to_dict(row):
    return {"id": row["id"], "title": row["title"], "content": row["content"]}


@bp.get("/health")
def health():
    return jsonify(status="ok")


@bp.get("/notes")
def list_notes():
    rows = get_db().execute("SELECT id, title, content FROM notes ORDER BY id").fetchall()
    return jsonify([note_to_dict(r) for r in rows])


@bp.post("/notes")
def create_note():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    content = data.get("content")
    if not isinstance(title, str) or not title.strip():
        abort(400, description="'title' is required")
    if not isinstance(content, str):
        abort(400, description="'content' must be a string")

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO notes (title, content) VALUES (?, ?)", (title.strip(), content)
    )
    conn.commit()
    return jsonify(id=cur.lastrowid, title=title.strip(), content=content), 201


@bp.get("/notes/<int:note_id>")
def get_note(note_id):
    row = get_db().execute(
        "SELECT id, title, content FROM notes WHERE id = ?", (note_id,)
    ).fetchone()
    if row is None:
        abort(404, description="note not found")
    return jsonify(note_to_dict(row))


@bp.get("/notes/search")
def search_notes():
    q = request.args.get("q", "")
    rows = get_db().execute(
        "SELECT id, title, content FROM notes WHERE title LIKE ? ORDER BY id",
        (f"%{q}%",),
    ).fetchall()
    return jsonify([note_to_dict(r) for r in rows])
