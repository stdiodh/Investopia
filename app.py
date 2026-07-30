from flask import Flask, render_template, request, redirect, url_for, jsonify
import math
import os
import pymysql

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]


class TradeError(Exception):
    def __init__(self, status_code, api_message, web_message):
        super().__init__(api_message)
        self.status_code = status_code
        self.api_message = api_message
        self.web_message = web_message


def _validate_api_quantity(quantity):
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("quantity must be a positive integer")
    return quantity


def _parse_form_quantity(quantity):
    if not isinstance(quantity, str) or not quantity.strip().isdigit():
        raise ValueError("quantity must be a positive integer")
    return _validate_api_quantity(int(quantity.strip()))


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


def _buy(cursor, symbol, quantity):
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


def _sell(cursor, symbol, quantity):
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


def get_connection():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        db=os.environ["DB_NAME"],
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            p.symbol,
            s.name,
            SUM(p.quantity) AS quantity,
            ROUND(SUM(p.quantity * p.buy_price) / SUM(p.quantity), 2) AS buy_price,
            s.last_price,
            ROUND(SUM(p.quantity) * s.last_price, 2) AS current_value,
            ROUND((s.last_price - (SUM(p.quantity * p.buy_price) / SUM(p.quantity))) 
                  / (SUM(p.quantity * p.buy_price) / SUM(p.quantity)) * 100, 2) AS change_rate
        FROM portfolio p
        JOIN stock s ON p.symbol = s.symbol
        WHERE p.quantity > 0
        GROUP BY p.symbol
    """)
    portfolio = cursor.fetchall()

    cursor.execute("""
        SELECT SUM(p.quantity * s.last_price) as total 
        FROM portfolio p 
        JOIN stock s ON p.symbol = s.symbol
        WHERE p.quantity > 0
    """)
    total = cursor.fetchone()['total'] or 0

    cursor.execute("SELECT asset FROM user_asset WHERE id=1")
    asset_row = cursor.fetchone()
    asset = asset_row['asset'] if asset_row else 0

    conn.close()

    return render_template('index.html', portfolio=portfolio, total=total, asset=asset)


@app.route('/stocks', methods=['GET', 'POST'])
def stocks():
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        action = request.form.get('action')

        try:
            quantity = _parse_form_quantity(request.form.get('quantity'))
        except ValueError:
            return redirect(
                url_for('stocks', msg="수량은 양의 정수여야 합니다.")
            )

        if not symbol:
            return redirect(url_for('stocks', msg="종목 코드가 필요합니다."))
        if action not in ('buy', 'sell'):
            return redirect(url_for('stocks', msg="잘못된 거래 요청입니다."))

        conn = get_connection()
        cursor = conn.cursor()
        try:
            try:
                if action == 'buy':
                    _buy(cursor, symbol, quantity)
                    message = f"{symbol} {quantity}주 매수 완료!"
                else:
                    _sell(cursor, symbol, quantity)
                    message = f"{symbol} {quantity}주 매도 완료!"
            except TradeError as error:
                message = error.web_message
            else:
                conn.commit()
        finally:
            conn.close()

        return redirect(url_for('stocks', msg=message))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT symbol, name, last_price, change_rate FROM stock")
    stocks = cursor.fetchall()

    cursor.execute("SELECT asset FROM user_asset WHERE id=1")
    asset_row = cursor.fetchone()
    asset = asset_row['asset'] if asset_row else 0

    message = request.args.get('msg', default=None)

    conn.close()
    return render_template('stocks.html', stocks=stocks, asset=asset, message=message)

@app.route('/asset', methods=['GET', 'POST'])
def asset_page():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT asset FROM user_asset WHERE id=1")
    row = cursor.fetchone()
    asset = row['asset'] if row else 0

    if request.method == 'POST':
        action = request.form.get('action')
        try:
            amount = float(request.form.get('amount', 0))
        except (TypeError, ValueError):
            conn.close()
            return "invalid amount", 400

        if (
            not math.isfinite(amount)
            or amount < 0
            or action not in ('add', 'set')
        ):
            conn.close()
            return "invalid amount", 400

        if action == 'add':
            asset += amount
        else:
            asset = amount

        cursor.execute("""
            INSERT INTO user_asset (id, asset, updated_at) 
            VALUES (1, %s, NOW()) 
            ON DUPLICATE KEY UPDATE asset=%s, updated_at=NOW()
        """, (asset, asset))

        conn.commit()
        conn.close()
        return redirect(url_for('asset_page'))

    conn.close()
    return render_template('asset.html', asset=asset)

@app.route('/api/buy', methods=['POST'])
def api_buy():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = {}
    symbol = data.get('symbol')
    quantity = data.get('quantity', 1)

    if not symbol:
        return jsonify({'result': 'fail', 'message': 'symbol missing'}), 400

    try:
        quantity = _validate_api_quantity(quantity)
    except ValueError as error:
        return jsonify({'result': 'fail', 'message': str(error)}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        try:
            _buy(cursor, symbol, quantity)
        except TradeError as error:
            return jsonify({
                'result': 'fail',
                'message': error.api_message,
            }), error.status_code
        conn.commit()
    finally:
        conn.close()

    return jsonify({'result': 'success', 'message': f'{symbol} {quantity}주 매수 완료!'})

@app.route('/api/sell', methods=['POST'])
def api_sell():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = {}
    symbol = data.get('symbol')
    quantity = data.get('quantity', 1)

    if not symbol:
        return jsonify({'result': 'fail', 'message': 'symbol missing'}), 400

    try:
        quantity = _validate_api_quantity(quantity)
    except ValueError as error:
        return jsonify({'result': 'fail', 'message': str(error)}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        try:
            _sell(cursor, symbol, quantity)
        except TradeError as error:
            return jsonify({
                'result': 'fail',
                'message': error.api_message,
            }), error.status_code
        conn.commit()
    finally:
        conn.close()

    return jsonify({'result': 'success', 'message': f'{symbol} {quantity}주 매도 완료!'})

if __name__ == '__main__':
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
