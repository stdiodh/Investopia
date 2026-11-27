"""Investopia 모의 투자 서버 패키지."""

import os
from pathlib import Path

from flask import Flask

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def create_app():
    from investopia.routes import api, web

    app = Flask(__name__, template_folder=str(PROJECT_ROOT / "templates"))
    app.secret_key = os.environ["FLASK_SECRET_KEY"]
    app.register_blueprint(web.bp)
    app.register_blueprint(api.bp)
    return app
