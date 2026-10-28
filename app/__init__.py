import os

from flask import Flask

from . import db, routes


def create_app(db_path=None):
    app = Flask(__name__)
    app.config["DATABASE"] = db_path or os.environ.get("NOTES_DB", "notes.db")

    app.register_blueprint(routes.bp)
    app.teardown_appcontext(db.close_db)

    with app.app_context():
        db.init_db()

    return app
