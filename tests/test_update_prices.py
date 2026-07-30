from datetime import datetime

import pytest
import requests

from static import update_prices


VALID_HTML = """
<html>
  <div class="wrap_company"><h2>삼성전자</h2></div>
  <p class="no_today"><span class="blind">71,500</span></p>
</html>
"""


class FakeResponse:
    def __init__(self, text, error=None):
        self.text = text
        self.error = error

    def raise_for_status(self):
        if self.error is not None:
            raise self.error


class RecordingCursor:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.executions = []

    def execute(self, sql, params=None):
        self.executions.append((" ".join(sql.lower().split()), params))
        if self.error is not None:
            raise self.error

    def fetchone(self):
        return self.result


class FakeConnection:
    def __init__(self, result=None, error=None):
        self.recording_cursor = RecordingCursor(result=result, error=error)
        self.commit_count = 0
        self.close_count = 0

    def cursor(self):
        return self.recording_cursor

    def commit(self):
        self.commit_count += 1

    def close(self):
        self.close_count += 1


def test_load_symbols_removes_blank_lines_and_comments(tmp_path):
    symbols_file = tmp_path / "symbols.txt"
    symbols_file.write_text(
        "\n# 관심 종목\n005930  # 삼성전자\n   \n000660# SK하이닉스\n",
        encoding="utf-8",
    )

    assert update_prices.load_symbols(symbols_file) == ["005930", "000660"]


def test_parse_stock_html_reads_company_name_and_comma_price():
    assert update_prices.parse_stock_html("005930", VALID_HTML) == {
        "symbol": "005930",
        "name": "삼성전자",
        "price": 71_500.0,
    }


def test_get_price_uses_naver_url_headers_and_explicit_timeout():
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return FakeResponse(VALID_HTML)

    result = update_prices.get_price_from_naver(
        "005930",
        http_get=fake_get,
        output=lambda message: None,
    )

    assert result["price"] == 71_500
    assert len(calls) == 1
    url, kwargs = calls[0]
    assert url == "https://finance.naver.com/item/main.nhn?code=005930"
    assert kwargs["headers"] == {"User-Agent": "Mozilla/5.0"}
    assert isinstance(kwargs["timeout"], (int, float))
    assert kwargs["timeout"] > 0


@pytest.mark.parametrize(
    "html",
    [
        "<p class='no_today'><span class='blind'>1,000</span></p>",
        "<div class='wrap_company'><h2>회사</h2></div>",
        """
        <div class="wrap_company"><h2>회사</h2></div>
        <p class="no_today"><span class="blind">가격없음</span></p>
        """,
        """
        <div class="wrap_company"><h2> </h2></div>
        <p class="no_today"><span class="blind">1,000</span></p>
        """,
        """
        <div class="wrap_company"><h2>회사</h2></div>
        <p class="no_today"><span class="blind">NaN</span></p>
        """,
        """
        <div class="wrap_company"><h2>회사</h2></div>
        <p class="no_today"><span class="blind">0</span></p>
        """,
        None,
    ],
)
def test_get_price_returns_none_for_missing_selectors_or_invalid_html(html):
    messages = []

    result = update_prices.get_price_from_naver(
        "000000",
        http_get=lambda *args, **kwargs: FakeResponse(html),
        output=messages.append,
    )

    assert result is None
    assert messages and "000000" in messages[0]


@pytest.mark.parametrize(
    "error",
    [
        requests.Timeout("timed out"),
        requests.ConnectionError("connection failed"),
        requests.HTTPError("bad response"),
    ],
)
def test_get_price_returns_none_for_http_errors(error):
    def fake_get(*args, **kwargs):
        if isinstance(error, requests.HTTPError):
            return FakeResponse(VALID_HTML, error=error)
        raise error

    assert (
        update_prices.get_price_from_naver(
            "005930",
            http_get=fake_get,
            output=lambda message: None,
        )
        is None
    )


@pytest.mark.parametrize(
    ("current_price", "previous_price", "expected"),
    [
        (110, None, 0.0),
        (110, 100, 10.0),
        (90, 100, -10.0),
        (100, 100, 0.0),
        (110, 0, 0.0),
    ],
)
def test_calculate_change_rate_handles_price_directions_and_zero(
    current_price, previous_price, expected
):
    assert (
        update_prices.calculate_change_rate(current_price, previous_price)
        == expected
    )


@pytest.mark.parametrize(
    ("stored_row", "expected"),
    [
        (None, None),
        (("71500",), 71_500.0),
        ({"last_price": 72_000}, 72_000.0),
    ],
)
def test_get_previous_price_uses_symbol_parameter_and_closes_connection(
    stored_row, expected
):
    connection = FakeConnection(result=stored_row)

    result = update_prices.get_previous_price(
        "005930",
        connection_factory=lambda: connection,
    )

    assert result == expected
    sql, params = connection.recording_cursor.executions[0]
    assert "select last_price" in sql
    assert "from stock" in sql
    assert params == ("005930",)
    assert connection.close_count == 1


def test_get_previous_price_propagates_database_error_and_closes_connection():
    connection = FakeConnection(error=RuntimeError("database unavailable"))

    with pytest.raises(RuntimeError, match="database unavailable"):
        update_prices.get_previous_price(
            "005930",
            connection_factory=lambda: connection,
        )
    assert connection.close_count == 1


def test_insert_or_update_verifies_upsert_contract_and_commits_once():
    connection = FakeConnection()
    updated_at = datetime(2026, 7, 30, 12, 34, 56)
    stock = {"symbol": "005930", "name": "삼성전자", "price": 71_500.0}

    result = update_prices.insert_or_update(
        stock,
        1.25,
        connection_factory=lambda: connection,
        now_factory=lambda: updated_at,
        output=lambda message: None,
    )

    assert result is True
    sql, params = connection.recording_cursor.executions[0]
    assert "insert into stock" in sql
    assert "on duplicate key update" in sql
    assert "name = values(name)" in sql
    assert "last_price = values(last_price)" in sql
    assert "change_rate = values(change_rate)" in sql
    assert params == ("005930", "삼성전자", 71_500.0, 1.25, updated_at)
    assert connection.commit_count == 1
    assert connection.close_count == 1


def test_insert_or_update_does_not_commit_after_database_error():
    connection = FakeConnection(error=RuntimeError("write failed"))
    messages = []

    result = update_prices.insert_or_update(
        {"symbol": "005930", "name": "삼성전자", "price": 71_500.0},
        0.0,
        connection_factory=lambda: connection,
        output=messages.append,
    )

    assert result is False
    assert connection.commit_count == 0
    assert connection.close_count == 1
    assert messages and "005930" in messages[0]
    assert "write failed" not in messages[0]


def test_update_once_continues_after_one_symbol_fails():
    saved = []

    def fetch_price(symbol):
        if symbol == "FAIL":
            raise requests.ConnectionError("offline")
        return {"symbol": symbol, "name": "정상 종목", "price": 110.0}

    def write_stock(stock, change_rate):
        saved.append((stock, change_rate))
        return True

    result = update_prices.update_once(
        ["FAIL", "OK"],
        price_fetcher=fetch_price,
        previous_price_fetcher=lambda symbol: 100.0,
        stock_writer=write_stock,
        output=lambda message: None,
    )

    assert result == [
        {
            "symbol": "OK",
            "name": "정상 종목",
            "price": 110.0,
            "change_rate": 10.0,
        }
    ]
    assert saved == [
        (
            {"symbol": "OK", "name": "정상 종목", "price": 110.0},
            10.0,
        )
    ]


def test_update_once_skips_fetch_and_database_failures_but_keeps_next_symbol():
    writes = []

    def fetch_price(symbol):
        if symbol == "NO_HTML":
            return None
        return {"symbol": symbol, "name": symbol, "price": 100.0}

    def write_stock(stock, change_rate):
        writes.append(stock["symbol"])
        return stock["symbol"] != "DB_FAIL"

    result = update_prices.update_once(
        ["NO_HTML", "DB_FAIL", "OK"],
        price_fetcher=fetch_price,
        previous_price_fetcher=lambda symbol: None,
        stock_writer=write_stock,
        output=lambda message: None,
    )

    assert [stock["symbol"] for stock in result] == ["OK"]
    assert writes == ["DB_FAIL", "OK"]


def test_update_once_skips_previous_price_error_and_keeps_next_symbol():
    writes = []

    def previous_price(symbol):
        if symbol == "READ_FAIL":
            raise RuntimeError("database unavailable")
        return 100.0

    result = update_prices.update_once(
        ["READ_FAIL", "OK"],
        price_fetcher=lambda symbol: {
            "symbol": symbol,
            "name": symbol,
            "price": 110.0,
        },
        previous_price_fetcher=previous_price,
        stock_writer=lambda stock, rate: (
            writes.append((stock["symbol"], rate)) or True
        ),
        output=lambda message: None,
    )

    assert [stock["symbol"] for stock in result] == ["OK"]
    assert writes == [("OK", 10.0)]


def test_update_once_uses_patchable_default_boundaries(monkeypatch):
    writes = []
    monkeypatch.setattr(
        update_prices,
        "get_price_from_naver",
        lambda symbol: {"symbol": symbol, "name": "회사", "price": 90.0},
    )
    monkeypatch.setattr(
        update_prices,
        "get_previous_price",
        lambda symbol: 100.0,
    )
    monkeypatch.setattr(
        update_prices,
        "insert_or_update",
        lambda stock, rate: writes.append((stock, rate)) or True,
    )

    result = update_prices.update_once(["005930"], output=lambda message: None)

    assert result[0]["change_rate"] == -10.0
    assert writes[0][0]["symbol"] == "005930"


def test_main_returns_when_symbols_file_is_missing(tmp_path, capsys):
    update_prices.main(tmp_path / "missing.txt")

    assert "종목 파일이 없습니다" in capsys.readouterr().out


def test_main_loads_symbols_before_starting_loop(tmp_path, monkeypatch):
    symbols_file = tmp_path / "symbols.txt"
    symbols_file.write_text("005930 # 삼성전자\n", encoding="utf-8")
    calls = []
    monkeypatch.setattr(update_prices, "run_forever", calls.append)

    update_prices.main(symbols_file)

    assert calls == [["005930"]]
