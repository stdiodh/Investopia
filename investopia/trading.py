"""매수·매도 규칙. 웹 폼과 REST API(Raspberry Pi)가 같은 함수를 호출한다.

호출한 쪽이 커서를 넘기고 commit·close를 맡는다. 규칙 위반은 TradeError로 알린다.
"""

import math


class TradeError(Exception):
    def __init__(self, status_code, api_message, web_message):
        super().__init__(api_message)
        self.status_code = status_code
        self.api_message = api_message
        self.web_message = web_message


def validate_api_quantity(quantity):
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("quantity must be a positive integer")
    return quantity


def parse_form_quantity(quantity):
    if not isinstance(quantity, str) or not quantity.strip().isdigit():
        raise ValueError("quantity must be a positive integer")
    return validate_api_quantity(int(quantity.strip()))


def _current_price(stock_row):
    if not stock_row:
        return None
    price = stock_row['last_price']
    try:
        if price is None or not math.isfinite(float(price)) or price <= 0:
            return None
    except (TypeError, ValueError):
        return None
    return price


def buy(cursor, symbol, quantity):
    cursor.execute("SELECT asset FROM user_asset WHERE id=1")
    asset_row = cursor.fetchone()
    asset = asset_row['asset'] if asset_row else 0

    cursor.execute("SELECT last_price FROM stock WHERE symbol=%s", (symbol,))
    stock_row = cursor.fetchone()
    if not stock_row:
        raise TradeError(404, "stock not found", "종목을 찾을 수 없습니다.")

    price = _current_price(stock_row)
    if price is None:
        raise TradeError(400, "price unavailable", "현재가를 확인할 수 없습니다.")

    total_cost = price * quantity
    if asset < total_cost:
        raise TradeError(400, "insufficient asset", "자산이 부족합니다.")

    cursor.execute(
        "SELECT quantity, buy_price FROM portfolio WHERE symbol=%s",
        (symbol,),
    )
    row = cursor.fetchone()

    if row:
        old_qty = row['quantity']
        old_price = row['buy_price']
        new_qty = old_qty + quantity
        avg_price = (old_qty * old_price + quantity * price) / new_qty
        cursor.execute(
            "UPDATE portfolio SET quantity=%s, buy_price=%s WHERE symbol=%s",
            (new_qty, avg_price, symbol),
        )
    else:
        cursor.execute(
            "INSERT INTO portfolio (symbol, quantity, buy_price) "
            "VALUES (%s, %s, %s)",
            (symbol, quantity, price),
        )

    cursor.execute(
        "UPDATE user_asset SET asset = asset - %s WHERE id=1",
        (total_cost,),
    )


def sell(cursor, symbol, quantity):
    cursor.execute(
        "SELECT quantity FROM portfolio WHERE symbol=%s",
        (symbol,),
    )
    row = cursor.fetchone()
    held_quantity = row['quantity'] if row else 0

    if held_quantity < quantity:
        raise TradeError(
            400,
            "insufficient quantity",
            "보유 수량이 부족합니다.",
        )

    cursor.execute("SELECT last_price FROM stock WHERE symbol=%s", (symbol,))
    stock_row = cursor.fetchone()
    price = _current_price(stock_row)
    if price is None:
        raise TradeError(
            400,
            "price unavailable",
            "현재가를 확인할 수 없습니다.",
        )

    cursor.execute("SELECT asset FROM user_asset WHERE id=1")
    if cursor.fetchone() is None:
        raise TradeError(
            400,
            "asset unavailable",
            "자산 정보를 확인할 수 없습니다.",
        )

    new_quantity = held_quantity - quantity
    if new_quantity > 0:
        cursor.execute(
            "UPDATE portfolio SET quantity=%s WHERE symbol=%s",
            (new_quantity, symbol),
        )
    else:
        cursor.execute("DELETE FROM portfolio WHERE symbol=%s", (symbol,))

    cursor.execute(
        "UPDATE user_asset SET asset = asset + %s WHERE id=1",
        (price * quantity,),
    )
