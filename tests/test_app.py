from dataclasses import dataclass

import pytest


import app as app_module


@dataclass
class ScriptStep:
    sql_tokens: tuple[str, ...]
    result: object = None
    params: object = None


class ScriptedCursor:
    def __init__(self, steps):
        self.steps = list(steps)
        self.current_result = None
        self.executions = []

    def execute(self, sql, params=None):
        assert self.steps, f"unexpected SQL: {sql}"
        step = self.steps.pop(0)
        normalized_sql = " ".join(sql.lower().split())
        for token in step.sql_tokens:
            assert token.lower() in normalized_sql
        assert params == step.params
        self.current_result = step.result
        self.executions.append((normalized_sql, params))

    def fetchone(self):
        return self.current_result

    def fetchall(self):
        return self.current_result


class FakeConnection:
    def __init__(self, steps):
        self.scripted_cursor = ScriptedCursor(steps)
        self.commit_count = 0
        self.close_count = 0

    def cursor(self):
        return self.scripted_cursor

    def commit(self):
        self.commit_count += 1

    def close(self):
        self.close_count += 1


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


@pytest.fixture
def use_db(monkeypatch):
    connections = []

    def install(*steps):
        connection = FakeConnection(steps)
        connections.append(connection)
        monkeypatch.setattr(app_module, "get_connection", lambda: connection)
        return connection

    yield install

    for connection in connections:
        assert connection.scripted_cursor.steps == []
        assert connection.close_count == 1


def step(*tokens, result=None, params=None):
    return ScriptStep(tokens, result=result, params=params)


def buy_steps(*, asset=10_000, stock=None, portfolio=None, quantity=1):
    symbol = "005930"
    price = stock["last_price"] if stock else None
    steps = [
        step("select asset", "user_asset", result={"asset": asset}),
        step(
            "select last_price",
            "from stock",
            result=stock,
            params=(symbol,),
        ),
    ]
    if (
        stock is None
        or price is None
        or price <= 0
        or asset < price * quantity
    ):
        return steps

    steps.append(
        step(
            "select quantity, buy_price",
            "from portfolio",
            result=portfolio,
            params=(symbol,),
        )
    )
    if portfolio:
        new_quantity = portfolio["quantity"] + quantity
        average_price = (
            portfolio["quantity"] * portfolio["buy_price"] + quantity * price
        ) / new_quantity
        steps.append(
            step(
                "update portfolio",
                "set quantity",
                "buy_price",
                params=(new_quantity, average_price, symbol),
            )
        )
    else:
        steps.append(
            step(
                "insert into portfolio",
                params=(symbol, quantity, price),
            )
        )
    steps.append(
        step(
            "update user_asset",
            "asset = asset -",
            params=(price * quantity,),
        )
    )
    return steps


def sell_steps(*, held=3, stock=None, quantity=1, asset_exists=True):
    symbol = "005930"
    steps = [
        step(
            "select quantity",
            "from portfolio",
            result={"quantity": held} if held is not None else None,
            params=(symbol,),
        )
    ]
    if held is None or held < quantity:
        return steps

    steps.append(
        step(
            "select last_price",
            "from stock",
            result=stock,
            params=(symbol,),
        )
    )
    if (
        stock is None
        or stock["last_price"] is None
        or stock["last_price"] <= 0
    ):
        return steps

    steps.append(
        step(
            "select asset",
            "from user_asset",
            result={"asset": 10_000} if asset_exists else None,
        )
    )
    if not asset_exists:
        return steps

    remaining = held - quantity
    if remaining:
        steps.append(
            step(
                "update portfolio",
                "set quantity",
                params=(remaining, symbol),
            )
        )
    else:
        steps.append(
            step(
                "delete from portfolio",
                params=(symbol,),
            )
        )
    steps.append(
        step(
            "update user_asset",
            "asset = asset +",
            params=(stock["last_price"] * quantity,),
        )
    )
    return steps


def test_api_buy_requires_symbol_without_opening_database(client, monkeypatch):
    monkeypatch.setattr(
        app_module,
        "get_connection",
        lambda: pytest.fail("database must not be opened"),
    )

    response = client.post("/api/buy", json={"quantity": 1})

    assert response.status_code == 400
    assert response.get_json() == {
        "result": "fail",
        "message": "symbol missing",
    }


@pytest.mark.parametrize("quantity", [0, -1, "1", 1.5, True, None])
def test_api_buy_rejects_non_positive_or_non_integer_quantity(
    client, monkeypatch, quantity
):
    monkeypatch.setattr(
        app_module,
        "get_connection",
        lambda: pytest.fail("database must not be opened"),
    )

    response = client.post(
        "/api/buy",
        json={"symbol": "005930", "quantity": quantity},
    )

    assert response.status_code == 400
    assert response.get_json()["result"] == "fail"


def test_api_buy_returns_not_found_without_commit(client, use_db):
    connection = use_db(
        *buy_steps(asset=10_000, stock=None),
    )

    response = client.post("/api/buy", json={"symbol": "005930"})

    assert response.status_code == 404
    assert response.get_json()["message"] == "stock not found"
    assert connection.commit_count == 0


@pytest.mark.parametrize(
    "price",
    [None, 0, -1, float("nan"), float("inf"), "invalid"],
)
def test_api_buy_without_valid_current_price_does_not_commit(
    client, use_db, price
):
    connection = use_db(
        step("select asset", "user_asset", result={"asset": 10_000}),
        step(
            "select last_price",
            "from stock",
            result={"last_price": price},
            params=("005930",),
        ),
    )

    response = client.post("/api/buy", json={"symbol": "005930"})

    assert response.status_code == 400
    assert response.get_json()["message"] == "price unavailable"
    assert connection.commit_count == 0


def test_api_buy_insufficient_asset_does_not_mutate_or_commit(client, use_db):
    connection = use_db(
        *buy_steps(asset=99, stock={"last_price": 100}, quantity=1),
    )

    response = client.post(
        "/api/buy",
        json={"symbol": "005930", "quantity": 1},
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "insufficient asset"
    assert connection.commit_count == 0
    assert len(connection.scripted_cursor.executions) == 2


def test_api_buy_new_position_uses_database_price_and_default_quantity(
    client, use_db
):
    connection = use_db(
        *buy_steps(
            asset=10_000,
            stock={"last_price": 120},
            portfolio=None,
            quantity=1,
        )
    )

    response = client.post(
        "/api/buy",
        json={"symbol": "005930", "price": 1},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "result": "success",
        "message": "005930 1주 매수 완료!",
    }
    assert connection.commit_count == 1


def test_api_buy_existing_position_updates_weighted_average(client, use_db):
    connection = use_db(
        *buy_steps(
            asset=10_000,
            stock={"last_price": 200},
            portfolio={"quantity": 10, "buy_price": 100},
            quantity=2,
        )
    )

    response = client.post(
        "/api/buy",
        json={"symbol": "005930", "quantity": 2, "price": 1},
    )

    assert response.status_code == 200
    assert connection.commit_count == 1


def test_api_sell_requires_symbol_without_opening_database(client, monkeypatch):
    monkeypatch.setattr(
        app_module,
        "get_connection",
        lambda: pytest.fail("database must not be opened"),
    )

    response = client.post("/api/sell", json={"quantity": 1})

    assert response.status_code == 400
    assert response.get_json()["message"] == "symbol missing"


@pytest.mark.parametrize("quantity", [0, -1, "1", 1.5, True, None])
def test_api_sell_rejects_non_positive_or_non_integer_quantity(
    client, monkeypatch, quantity
):
    monkeypatch.setattr(
        app_module,
        "get_connection",
        lambda: pytest.fail("database must not be opened"),
    )

    response = client.post(
        "/api/sell",
        json={"symbol": "005930", "quantity": quantity},
    )

    assert response.status_code == 400
    assert response.get_json()["result"] == "fail"


@pytest.mark.parametrize("held", [None, 1])
def test_api_sell_unheld_or_insufficient_position_does_not_commit(
    client, use_db, held
):
    connection = use_db(*sell_steps(held=held, quantity=2))

    response = client.post(
        "/api/sell",
        json={"symbol": "005930", "quantity": 2},
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "insufficient quantity"
    assert connection.commit_count == 0


def test_api_sell_partial_position_uses_database_price(client, use_db):
    connection = use_db(
        *sell_steps(held=3, stock={"last_price": 250}, quantity=2)
    )

    response = client.post(
        "/api/sell",
        json={"symbol": "005930", "quantity": 2, "price": 1},
    )

    assert response.status_code == 200
    assert response.get_json()["result"] == "success"
    assert connection.commit_count == 1


def test_api_sell_full_position_deletes_portfolio_row(client, use_db):
    connection = use_db(
        *sell_steps(held=2, stock={"last_price": 250}, quantity=2)
    )

    response = client.post(
        "/api/sell",
        json={"symbol": "005930", "quantity": 2},
    )

    assert response.status_code == 200
    assert connection.commit_count == 1


def test_api_sell_uses_default_quantity(client, use_db):
    connection = use_db(
        *sell_steps(held=2, stock={"last_price": 250}, quantity=1)
    )

    response = client.post("/api/sell", json={"symbol": "005930"})

    assert response.status_code == 200
    assert response.get_json()["message"] == "005930 1주 매도 완료!"
    assert connection.commit_count == 1


@pytest.mark.parametrize(
    "stock",
    [
        None,
        {"last_price": None},
        {"last_price": 0},
        {"last_price": -1},
        {"last_price": float("nan")},
        {"last_price": float("inf")},
        {"last_price": "invalid"},
    ],
)
def test_api_sell_without_current_price_does_not_mutate_or_commit(
    client, use_db, stock
):
    connection = use_db(
        step(
            "select quantity",
            "from portfolio",
            result={"quantity": 3},
            params=("005930",),
        ),
        step(
            "select last_price",
            "from stock",
            result=stock,
            params=("005930",),
        ),
    )

    response = client.post(
        "/api/sell",
        json={"symbol": "005930", "quantity": 2},
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "price unavailable"
    assert connection.commit_count == 0
    assert len(connection.scripted_cursor.executions) == 2


def test_api_sell_without_asset_row_does_not_mutate_or_commit(client, use_db):
    connection = use_db(
        *sell_steps(
            held=3,
            stock={"last_price": 250},
            quantity=2,
            asset_exists=False,
        )
    )

    response = client.post(
        "/api/sell",
        json={"symbol": "005930", "quantity": 2},
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "asset unavailable"
    assert connection.commit_count == 0
    assert len(connection.scripted_cursor.executions) == 3


@pytest.mark.parametrize("endpoint", ["/api/buy", "/api/sell"])
def test_trade_api_rejects_non_object_json(client, monkeypatch, endpoint):
    monkeypatch.setattr(
        app_module,
        "get_connection",
        lambda: pytest.fail("database must not be opened"),
    )

    response = client.post(endpoint, json=[])

    assert response.status_code == 400
    assert response.get_json()["message"] == "symbol missing"


def test_index_get_renders_portfolio_and_assets(client, use_db):
    portfolio = [
        {
            "symbol": "005930",
            "name": "삼성전자",
            "quantity": 2,
            "buy_price": 100,
            "last_price": 120,
            "current_value": 240,
            "change_rate": 20,
        }
    ]
    use_db(
        step(
            "from portfolio p",
            "group by p.symbol",
            result=portfolio,
        ),
        step(
            "select sum",
            "as total",
            result={"total": 240},
        ),
        step(
            "select asset",
            "user_asset",
            result={"asset": 1_000},
        ),
    )

    response = client.get("/")

    assert response.status_code == 200
    assert "내 포트폴리오".encode() in response.data
    assert "삼성전자".encode() in response.data
    assert "1240".encode() in response.data


def test_stocks_get_renders_database_prices_and_asset(client, use_db):
    use_db(
        step(
            "select symbol, name, last_price, change_rate",
            result=[
                {
                    "symbol": "005930",
                    "name": "삼성전자",
                    "last_price": 72_000,
                    "change_rate": 1.5,
                }
            ],
        ),
        step(
            "select asset",
            "user_asset",
            result={"asset": 100_000},
        ),
    )

    response = client.get("/stocks")

    assert response.status_code == 200
    assert "종목 리스트".encode() in response.data
    assert "삼성전자".encode() in response.data
    assert b"72000" in response.data


def test_stocks_post_buy_ignores_tampered_hidden_price(client, use_db):
    connection = use_db(
        *buy_steps(
            asset=10_000,
            stock={"last_price": 200},
            portfolio=None,
            quantity=2,
        )
    )

    response = client.post(
        "/stocks",
        data={
            "symbol": "005930",
            "price": "1",
            "quantity": "2",
            "action": "buy",
        },
    )

    assert response.status_code == 302
    assert "msg=005930+2".encode() in response.headers["Location"].encode()
    assert connection.commit_count == 1


def test_stocks_post_buy_failure_does_not_commit(client, use_db):
    connection = use_db(
        *buy_steps(
            asset=100,
            stock={"last_price": 200},
            quantity=1,
        )
    )

    response = client.post(
        "/stocks",
        data={
            "symbol": "005930",
            "price": "1",
            "quantity": "1",
            "action": "buy",
        },
    )

    assert response.status_code == 302
    assert connection.commit_count == 0
    assert "%EC%9E%90%EC%82%B0" in response.headers["Location"]


def test_stocks_post_sell_uses_database_price(client, use_db):
    connection = use_db(
        *sell_steps(held=3, stock={"last_price": 250}, quantity=1)
    )

    response = client.post(
        "/stocks",
        data={
            "symbol": "005930",
            "price": "999999999",
            "quantity": "1",
            "action": "sell",
        },
    )

    assert response.status_code == 302
    assert connection.commit_count == 1


def test_stocks_post_sell_failure_does_not_commit(client, use_db):
    connection = use_db(*sell_steps(held=1, quantity=2))

    response = client.post(
        "/stocks",
        data={
            "symbol": "005930",
            "price": "250",
            "quantity": "2",
            "action": "sell",
        },
    )

    assert response.status_code == 302
    assert connection.commit_count == 0
    assert "%EB%B3%B4%EC%9C%A0" in response.headers["Location"]


@pytest.mark.parametrize(
    "form",
    [
        {"symbol": "005930", "quantity": "0", "action": "buy"},
        {"symbol": "005930", "quantity": "invalid", "action": "buy"},
        {"symbol": "005930", "action": "buy"},
        {"quantity": "1", "action": "buy"},
        {"symbol": "005930", "quantity": "1", "action": "hold"},
    ],
)
def test_stocks_post_rejects_invalid_request_without_opening_database(
    client, monkeypatch, form
):
    monkeypatch.setattr(
        app_module,
        "get_connection",
        lambda: pytest.fail("database must not be opened"),
    )

    response = client.post("/stocks", data=form)

    assert response.status_code == 302
    assert "msg=" in response.headers["Location"]


def test_asset_get_renders_current_asset(client, use_db):
    use_db(
        step(
            "select asset",
            "user_asset",
            result={"asset": 12_000},
        )
    )

    response = client.get("/asset")

    assert response.status_code == 200
    assert "가상 자산 관리".encode() in response.data
    assert "12,000".encode() in response.data


@pytest.mark.parametrize(
    ("action", "amount", "stored"),
    [("add", "500", 1_500.0), ("set", "500", 500.0)],
)
def test_asset_post_add_or_set(client, use_db, action, amount, stored):
    connection = use_db(
        step(
            "select asset",
            "user_asset",
            result={"asset": 1_000},
        ),
        step(
            "insert into user_asset",
            "on duplicate key update",
            params=(stored, stored),
        ),
    )

    response = client.post(
        "/asset",
        data={"action": action, "amount": amount},
    )

    assert response.status_code == 302
    assert connection.commit_count == 1


@pytest.mark.parametrize(
    ("action", "amount"),
    [
        ("set", "-1"),
        ("set", "not-a-number"),
        ("set", "nan"),
        ("set", "inf"),
        ("invalid", "1"),
    ],
)
def test_asset_post_rejects_invalid_amount_or_action_without_commit(
    client, use_db, action, amount
):
    connection = use_db(
        step(
            "select asset",
            "user_asset",
            result={"asset": 1_000},
        )
    )

    response = client.post(
        "/asset",
        data={"action": action, "amount": amount},
    )

    assert response.status_code == 400
    assert connection.commit_count == 0
