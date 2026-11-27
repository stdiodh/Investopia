"""MariaDB 연결 설정. 웹 서버·시세 수집기·Raspberry Pi 제어기가 같은 환경 변수를 읽는다."""

import os

import pymysql


def connection_settings():
    """실제 연결 직전에 환경 변수를 읽어, import 시점에는 설정이 없어도 된다."""
    return {
        "host": os.environ["DB_HOST"],
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "db": os.environ["DB_NAME"],
        "charset": "utf8",
    }


def connect():
    """행을 튜플로 돌려주는 연결. 시세 수집기가 사용한다."""
    return pymysql.connect(**connection_settings())


def connect_dict():
    """행을 dict로 돌려주는 연결. 웹 서버와 Raspberry Pi 제어기가 사용한다."""
    return pymysql.connect(**connection_settings(), cursorclass=pymysql.cursors.DictCursor)
