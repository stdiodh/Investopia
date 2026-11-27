"""Flask 웹 서버 실행 진입점. 라우트와 거래 규칙은 investopia 패키지에 있다."""

import os

from investopia import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
