import os

from flask import Flask

from . import db, routes


def create_app(db_path=None):
    app = Flask(__name__)
    app.config["DATABASE"] = db_path or os.environ.get("NOTES_DB", "notes.db")

    app.register_blueprint(routes.bp)
    app.teardown_appcontext(db.close_db)

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        response.headers["Cache-Control"] = "no-store"
        return response

    with app.app_context():
        db.init_db()

    return app
