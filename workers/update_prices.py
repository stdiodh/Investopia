"""네이버 금융에서 종목 시세를 읽어 데이터베이스에 갱신한다."""

from datetime import datetime
import math
import os
from pathlib import Path
import time

from bs4 import BeautifulSoup
import pymysql
import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SYMBOLS_FILE = PROJECT_ROOT / "config" / "symbols.txt"
NAVER_FINANCE_URL = "https://finance.naver.com/item/main.nhn?code={symbol}"
HTTP_TIMEOUT = 10
UPDATE_INTERVAL_SECONDS = 30


def get_db_config():
    """실제 DB 연결 직전에 환경 설정을 읽는다."""
    return {
        "host": os.environ["DB_HOST"],
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "db": os.environ["DB_NAME"],
        "charset": "utf8",
    }


def get_connection():
    return pymysql.connect(**get_db_config())


def load_symbols(path=SYMBOLS_FILE):
    """빈 줄과 ``#`` 뒤의 주석을 제외한 종목 코드를 읽는다."""
    symbols = []
    with Path(path).open(encoding="utf-8") as symbols_file:
        for line in symbols_file:
            symbol = line.partition("#")[0].strip()
            if symbol:
                symbols.append(symbol)
    return symbols


def parse_stock_html(symbol, html):
    """네이버 금융 종목 HTML에서 종목명과 현재가를 추출한다."""
    soup = BeautifulSoup(html, "html.parser")
    name_element = soup.select_one("div.wrap_company h2")
    price_element = soup.select_one("p.no_today span.blind")
    if name_element is None or price_element is None:
        raise ValueError("required stock selector missing")

    name = name_element.get_text(strip=True)
    price_text = price_element.get_text(strip=True).replace(",", "")
    if not name or not price_text:
        raise ValueError("empty stock name or price")

    try:
        price = float(price_text)
    except ValueError as exc:
        raise ValueError("invalid stock price") from exc
    if not math.isfinite(price) or price <= 0:
        raise ValueError("invalid stock price")

    return {"symbol": symbol, "name": name, "price": price}


def get_price_from_naver(symbol, http_get=None, output=print):
    """한 종목을 요청한다. 요청 또는 파싱 실패 시 ``None``을 반환한다."""
    if http_get is None:
        http_get = requests.get

    try:
        response = http_get(
            NAVER_FINANCE_URL.format(symbol=symbol),
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=HTTP_TIMEOUT,
        )
        response.raise_for_status()
        return parse_stock_html(symbol, response.text)
    except (requests.RequestException, TypeError, ValueError, AttributeError) as exc:
        output(f"[오류] {symbol}: {exc}")
        return None


def get_previous_price(symbol, connection_factory=None):
    """저장된 직전 가격을 읽고, 저장된 값이 없으면 ``None``을 반환한다."""
    if connection_factory is None:
        connection_factory = get_connection

    connection = None
    try:
        connection = connection_factory()
        cursor = connection.cursor()
        cursor.execute("SELECT last_price FROM stock WHERE symbol = %s", (symbol,))
        row = cursor.fetchone()
        if row is None:
            return None
        value = row["last_price"] if isinstance(row, dict) else row[0]
        return float(value)
    finally:
        if connection is not None:
            connection.close()


def calculate_change_rate(current_price, previous_price):
    """직전 가격이 없거나 0이면 0%, 그 외에는 소수 둘째 자리까지 계산한다."""
    if previous_price is None or previous_price == 0:
        return 0.0
    return round(((current_price - previous_price) / previous_price) * 100, 2)


def insert_or_update(
    stock_data,
    change_rate,
    connection_factory=None,
    now_factory=None,
    output=print,
):
    """한 종목을 upsert하고 성공 여부를 반환한다."""
    if connection_factory is None:
        connection_factory = get_connection
    if now_factory is None:
        now_factory = datetime.now

    connection = None
    try:
        connection = connection_factory()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO stock (symbol, name, last_price, change_rate, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                last_price = VALUES(last_price),
                change_rate = VALUES(change_rate),
                updated_at = VALUES(updated_at)
            """,
            (
                stock_data["symbol"],
                stock_data["name"],
                stock_data["price"],
                change_rate,
                now_factory(),
            ),
        )
        connection.commit()
        return True
    except Exception:
        output(f"[DB 오류] {stock_data['symbol']}: 저장하지 못했습니다.")
        return False
    finally:
        if connection is not None:
            connection.close()


def update_once(
    symbols,
    price_fetcher=None,
    previous_price_fetcher=None,
    stock_writer=None,
    output=print,
):
    """모든 종목을 한 번 갱신하고 성공적으로 저장한 결과를 반환한다."""
    if price_fetcher is None:
        price_fetcher = get_price_from_naver
    if previous_price_fetcher is None:
        previous_price_fetcher = get_previous_price
    if stock_writer is None:
        stock_writer = insert_or_update

    updated = []
    for symbol in symbols:
        try:
            stock_data = price_fetcher(symbol)
            if stock_data is None:
                continue
            previous_price = previous_price_fetcher(symbol)
            change_rate = calculate_change_rate(stock_data["price"], previous_price)
            if not stock_writer(stock_data, change_rate):
                continue
        except Exception as exc:
            output(f"[오류] {symbol}: {exc}")
            continue

        result = {**stock_data, "change_rate": change_rate}
        updated.append(result)
        output(
            f"  {stock_data['name']:<10} | "
            f"{stock_data['price']:>8,.0f}원 | {change_rate:+.2f}%"
        )
    return updated


def run_forever(symbols, interval=UPDATE_INTERVAL_SECONDS, sleep_fn=None):
    """운영 환경에서 1회 갱신을 정해진 간격으로 반복한다."""
    if sleep_fn is None:
        sleep_fn = time.sleep

    print("주가 업데이트 시작 (30초 마다 갱신)")
    while True:
        print(f"\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 기준:")
        update_once(symbols)
        sleep_fn(interval)


def main(symbols_file=SYMBOLS_FILE):
    try:
        symbols = load_symbols(symbols_file)
    except FileNotFoundError:
        print(f"❌ 종목 파일이 없습니다: {symbols_file}")
        return
    run_forever(symbols)
