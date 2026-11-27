import pymysql

from investopia import db


ENV = {
    "DB_HOST": "db.local",
    "DB_USER": "investopia",
    "DB_PASSWORD": "pytest-only",
    "DB_NAME": "stock_db",
}


def test_connection_settings_read_environment_with_default_port(monkeypatch):
    for key, value in ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("DB_PORT", raising=False)

    assert db.connection_settings() == {
        "host": "db.local",
        "port": 3306,
        "user": "investopia",
        "password": "pytest-only",
        "db": "stock_db",
        "charset": "utf8",
    }


def test_connect_and_connect_dict_differ_only_by_cursor_class(monkeypatch):
    for key, value in ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("DB_PORT", "3307")
    calls = []
    monkeypatch.setattr(pymysql, "connect", lambda **kwargs: calls.append(kwargs) or "conn")

    assert db.connect() == "conn"
    assert db.connect_dict() == "conn"

    assert calls[0]["port"] == 3307
    assert "cursorclass" not in calls[0]
    assert calls[1] == {**calls[0], "cursorclass": pymysql.cursors.DictCursor}
