from flask import Flask, render_template, request, redirect, url_for, jsonify
import pymysql

app = Flask(__name__)
app.secret_key = "stocksecret"

def get_connection():
    return pymysql.connect(
        host='192.173.0.41',
        user='root',
        password='qwer1230',
        db='stock_db',
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
    conn = get_connection()
    cursor = conn.cursor()

    message = None

    if request.method == 'POST':
        symbol = request.form['symbol']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        action = request.form['action']

        cursor.execute("SELECT asset FROM user_asset WHERE id=1")
        asset_row = cursor.fetchone()
        asset = asset_row['asset'] if asset_row else 0

        if action == 'buy':
            total_cost = price * quantity
            if asset >= total_cost:
                cursor.execute("SELECT quantity, buy_price FROM portfolio WHERE symbol=%s", (symbol,))
                row = cursor.fetchone()

                if row:
                    old_qty = row['quantity']
                    old_price = row['buy_price']
                    new_qty = old_qty + quantity
                    avg_price = (old_qty * old_price + quantity * price) / new_qty

                    cursor.execute("""
                        UPDATE portfolio 
                        SET quantity = %s, buy_price = %s 
                        WHERE symbol = %s
                    """, (new_qty, avg_price, symbol))
                else:
                    cursor.execute("""
                        INSERT INTO portfolio (symbol, quantity, buy_price) 
                        VALUES (%s, %s, %s)
                    """, (symbol, quantity, price))

                cursor.execute("UPDATE user_asset SET asset = asset - %s WHERE id=1", (total_cost,))
                message = f"{symbol} {quantity}주 매수 완료!"
            else:
                message = "자산이 부족합니다."

        elif action == 'sell':
            cursor.execute("SELECT quantity FROM portfolio WHERE symbol=%s", (symbol,))
            row = cursor.fetchone()
            held_quantity = row['quantity'] if row else 0

            if held_quantity >= quantity:
                new_quantity = held_quantity - quantity

                if new_quantity > 0:
                    cursor.execute("UPDATE portfolio SET quantity = %s WHERE symbol=%s", (new_quantity, symbol))
                else:
                    cursor.execute("DELETE FROM portfolio WHERE symbol=%s", (symbol,))

                cursor.execute("UPDATE user_asset SET asset = asset + %s WHERE id=1", (price * quantity,))
                message = f"{symbol} {quantity}주 매도 완료!"
            else:
                message = "보유 수량이 부족합니다."

        conn.commit()
        conn.close()
        return redirect(url_for('stocks', msg=message))

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
        amount = float(request.form.get('amount', 0))

        if action == 'add':
            asset += amount
        elif action == 'set':
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
    data = request.get_json()
    symbol = data.get('symbol')
    quantity = data.get('quantity', 1)

    if not symbol:
        return jsonify({'result': 'fail', 'message': 'symbol missing'}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT asset FROM user_asset WHERE id=1")
    asset_row = cursor.fetchone()
    asset = asset_row['asset'] if asset_row else 0

    cursor.execute("SELECT last_price FROM stock WHERE symbol=%s", (symbol,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'result': 'fail', 'message': 'stock not found'}), 404

    price = row['last_price']
    total_cost = price * quantity

    if asset < total_cost:
        conn.close()
        return jsonify({'result': 'fail', 'message': 'insufficient asset'}), 400

    cursor.execute("SELECT quantity, buy_price FROM portfolio WHERE symbol=%s", (symbol,))
    row = cursor.fetchone()

    if row:
        old_qty = row['quantity']
        old_price = row['buy_price']
        new_qty = old_qty + quantity
        avg_price = (old_qty * old_price + quantity * price) / new_qty
        cursor.execute("UPDATE portfolio SET quantity=%s, buy_price=%s WHERE symbol=%s", (new_qty, avg_price, symbol))
    else:
        cursor.execute("INSERT INTO portfolio (symbol, quantity, buy_price) VALUES (%s, %s, %s)", (symbol, quantity, price))

    cursor.execute("UPDATE user_asset SET asset = asset - %s WHERE id=1", (total_cost,))
    conn.commit()
    conn.close()

    return jsonify({'result': 'success', 'message': f'{symbol} {quantity}주 매수 완료!'})

@app.route('/api/sell', methods=['POST'])
def api_sell():
    data = request.get_json()
    symbol = data.get('symbol')
    quantity = data.get('quantity', 1)

    if not symbol:
        return jsonify({'result': 'fail', 'message': 'symbol missing'}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT quantity FROM portfolio WHERE symbol=%s", (symbol,))
    row = cursor.fetchone()
    held_quantity = row['quantity'] if row else 0

    if held_quantity < quantity:
        conn.close()
        return jsonify({'result': 'fail', 'message': 'insufficient quantity'}), 400

    cursor.execute("SELECT last_price FROM stock WHERE symbol=%s", (symbol,))
    row = cursor.fetchone()
    price = row['last_price'] if row else 0

    new_quantity = held_quantity - quantity
    if new_quantity > 0:
        cursor.execute("UPDATE portfolio SET quantity=%s WHERE symbol=%s", (new_quantity, symbol))
    else:
        cursor.execute("DELETE FROM portfolio WHERE symbol=%s", (symbol,))

    cursor.execute("UPDATE user_asset SET asset = asset + %s WHERE id=1", (price * quantity,))
    conn.commit()
    conn.close()

    return jsonify({'result': 'success', 'message': f'{symbol} {quantity}주 매도 완료!'})

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
