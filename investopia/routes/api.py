"""Raspberry Pi 버튼과 외부 클라이언트가 호출하는 매수·매도 REST API."""

from flask import Blueprint, jsonify, request

from investopia import db, trading

bp = Blueprint("api", __name__)


@bp.route('/api/buy', methods=['POST'])
def api_buy():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = {}
    symbol = data.get('symbol')
    quantity = data.get('quantity', 1)

    if not symbol:
        return jsonify({'result': 'fail', 'message': 'symbol missing'}), 400

    try:
        quantity = trading.validate_api_quantity(quantity)
    except ValueError as error:
        return jsonify({'result': 'fail', 'message': str(error)}), 400

    conn = db.connect_dict()
    cursor = conn.cursor()
    try:
        try:
            trading.buy(cursor, symbol, quantity)
        except trading.TradeError as error:
            return jsonify({
                'result': 'fail',
                'message': error.api_message,
            }), error.status_code
        conn.commit()
    finally:
        conn.close()

    return jsonify({'result': 'success', 'message': f'{symbol} {quantity}주 매수 완료!'})

@bp.route('/api/sell', methods=['POST'])
def api_sell():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = {}
    symbol = data.get('symbol')
    quantity = data.get('quantity', 1)

    if not symbol:
        return jsonify({'result': 'fail', 'message': 'symbol missing'}), 400

    try:
        quantity = trading.validate_api_quantity(quantity)
    except ValueError as error:
        return jsonify({'result': 'fail', 'message': str(error)}), 400

    conn = db.connect_dict()
    cursor = conn.cursor()
    try:
        try:
            trading.sell(cursor, symbol, quantity)
        except trading.TradeError as error:
            return jsonify({
                'result': 'fail',
                'message': error.api_message,
            }), error.status_code
        conn.commit()
    finally:
        conn.close()

    return jsonify({'result': 'success', 'message': f'{symbol} {quantity}주 매도 완료!'})
