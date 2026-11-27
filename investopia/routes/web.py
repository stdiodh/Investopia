"""브라우저 화면: 자산 요약, 종목 목록과 거래 폼, 현금 자산 설정."""

import math

from flask import Blueprint, redirect, render_template, request, url_for

from investopia import db, trading

bp = Blueprint("web", __name__)


@bp.route('/')
def index():
    conn = db.connect_dict()
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


@bp.route('/stocks', methods=['GET', 'POST'])
def stocks():
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        action = request.form.get('action')

        try:
            quantity = trading.parse_form_quantity(request.form.get('quantity'))
        except ValueError:
            return redirect(
                url_for('web.stocks', msg="수량은 양의 정수여야 합니다.")
            )

        if not symbol:
            return redirect(url_for('web.stocks', msg="종목 코드가 필요합니다."))
        if action not in ('buy', 'sell'):
            return redirect(url_for('web.stocks', msg="잘못된 거래 요청입니다."))

        conn = db.connect_dict()
        cursor = conn.cursor()
        try:
            try:
                if action == 'buy':
                    trading.buy(cursor, symbol, quantity)
                    message = f"{symbol} {quantity}주 매수 완료!"
                else:
                    trading.sell(cursor, symbol, quantity)
                    message = f"{symbol} {quantity}주 매도 완료!"
            except trading.TradeError as error:
                message = error.web_message
            else:
                conn.commit()
        finally:
            conn.close()

        return redirect(url_for('web.stocks', msg=message))

    conn = db.connect_dict()
    cursor = conn.cursor()

    cursor.execute("SELECT symbol, name, last_price, change_rate FROM stock")
    stocks = cursor.fetchall()

    cursor.execute("SELECT asset FROM user_asset WHERE id=1")
    asset_row = cursor.fetchone()
    asset = asset_row['asset'] if asset_row else 0

    message = request.args.get('msg', default=None)

    conn.close()
    return render_template('stocks.html', stocks=stocks, asset=asset, message=message)

@bp.route('/asset', methods=['GET', 'POST'])
def asset_page():
    conn = db.connect_dict()
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
        return redirect(url_for('web.asset_page'))

    conn.close()
    return render_template('asset.html', asset=asset)
