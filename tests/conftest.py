import os
import socket

import pytest


os.environ.setdefault("FLASK_SECRET_KEY", "pytest-only")


@pytest.fixture(autouse=True)
def block_external_network(monkeypatch):
    def fail_connect(*args, **kwargs):
        raise AssertionError("external network access is disabled in tests")

    monkeypatch.setattr(socket.socket, "connect", fail_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", fail_connect)
    monkeypatch.setattr(socket, "getaddrinfo", fail_connect)
