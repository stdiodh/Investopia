"""조이스틱·버튼 입력으로 주문 API를 호출하고 LCD·LED에 시세를 보여 주는 Raspberry Pi 제어 루프."""

import os
import time

import requests

from investopia import db
from investopia.device.lcd import LCD


VRX, VRY, SW = 16, 20, 4
BUTTON_BUY, BUTTON_SELL, BUTTON_BUZZER_OFF = 19, 13, 12
BUZZER, LED_UP, LED_DOWN = 26, 6, 5

SERVER_URL = os.getenv("INVESTOPIA_SERVER_URL", "http://127.0.0.1:5000")
REQUEST_TIMEOUT = 5


def fetch_data(connection_factory=None):
    connection_factory = connection_factory or db.connect_dict
    connection = connection_factory()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT symbol, name, last_price, change_rate FROM stock")
        stocks = cursor.fetchall()
        cursor.execute("SELECT asset FROM user_asset WHERE id=1")
        asset = cursor.fetchone()["asset"]
        return stocks, asset
    finally:
        connection.close()


def display_stock(stock, asset, lcd_device):
    lcd_device.clear()
    symbol = stock["symbol"][:6]
    price = f"{stock['last_price']:.1f}"
    rate = f"{stock['change_rate']:+.2f}"
    lcd_device.setCursor(0, 0)
    lcd_device.message(f"{symbol:<6} {price:>8}")
    lcd_device.setCursor(0, 1)
    lcd_device.message(f"{rate}%  ₩{int(asset):,}")


def update_total_change_leds(portfolio, gpio):
    total_change = sum(float(stock["change_rate"] or 0) for stock in portfolio)
    gpio.output(LED_UP, total_change > 0)
    gpio.output(LED_DOWN, total_change < 0)


def is_pressed(pin, gpio):
    return gpio.input(pin) == gpio.LOW


def send_order(
    symbol,
    action,
    http_client=None,
    server_url=SERVER_URL,
    timeout=REQUEST_TIMEOUT,
):
    http_client = http_client or requests
    try:
        response = http_client.post(
            f"{server_url}/api/{action}",
            json={"symbol": symbol, "quantity": 1},
            timeout=timeout,
        )
        if response.ok:
            print(f"{action.upper()} 성공: {response.json()['message']}")
            return True

        print(f"{action.upper()} 실패: {response.json().get('message', '오류')}")
        return False
    except requests.RequestException as error:
        print(f"{action.upper()} 요청 오류: {error}")
        return False


def process_iteration(
    stocks,
    asset,
    current_index,
    *,
    gpio,
    lcd_device,
    http_client=None,
    server_url=SERVER_URL,
    sleep_fn=time.sleep,
):
    current_index %= len(stocks)
    update_total_change_leds(stocks, gpio)

    if is_pressed(VRY, gpio):
        current_index = (current_index + 1) % len(stocks)
        sleep_fn(0.3)
    elif is_pressed(VRX, gpio):
        current_index = (current_index - 1) % len(stocks)
        sleep_fn(0.3)

    selected_stock = stocks[current_index]
    display_stock(selected_stock, asset, lcd_device)

    if is_pressed(BUTTON_BUY, gpio):
        send_order(
            selected_stock["symbol"],
            "buy",
            http_client=http_client,
            server_url=server_url,
        )
        sleep_fn(0.3)

    if is_pressed(BUTTON_SELL, gpio):
        send_order(
            selected_stock["symbol"],
            "sell",
            http_client=http_client,
            server_url=server_url,
        )
        sleep_fn(0.3)

    if is_pressed(BUTTON_BUZZER_OFF, gpio):
        gpio.output(BUZZER, gpio.LOW)

    sleep_fn(0.1)
    return current_index


def main_loop(
    *,
    gpio,
    lcd_device,
    fetch_data_fn=fetch_data,
    http_client=None,
    server_url=SERVER_URL,
    sleep_fn=time.sleep,
    iterations=None,
):
    current_index = 0
    completed = 0
    while iterations is None or completed < iterations:
        completed += 1
        stocks, asset = fetch_data_fn()
        if not stocks:
            lcd_device.clear()
            lcd_device.message("No stock data")
            sleep_fn(1)
            continue

        current_index = process_iteration(
            stocks,
            asset,
            current_index,
            gpio=gpio,
            lcd_device=lcd_device,
            http_client=http_client,
            server_url=server_url,
            sleep_fn=sleep_fn,
        )

    return current_index


def setup_gpio(gpio):
    gpio.setmode(gpio.BCM)
    gpio.setwarnings(False)
    gpio.setup([VRX, VRY], gpio.IN)
    gpio.setup(
        [SW, BUTTON_BUY, BUTTON_SELL, BUTTON_BUZZER_OFF],
        gpio.IN,
        pull_up_down=gpio.PUD_UP,
    )
    gpio.setup([BUZZER, LED_UP, LED_DOWN], gpio.OUT)


def load_gpio():
    import RPi.GPIO as GPIO

    return GPIO


def run(
    *,
    gpio=None,
    lcd_factory=LCD,
    fetch_data_fn=fetch_data,
    http_client=None,
    server_url=SERVER_URL,
    sleep_fn=time.sleep,
    iterations=None,
):
    gpio = gpio or load_gpio()
    lcd_device = None
    try:
        setup_gpio(gpio)
        lcd_device = lcd_factory(GPIO=gpio, sleep_fn=sleep_fn)
        lcd_device.begin(16, 2)
        lcd_device.clear()
        lcd_device.message("System Booting...")
        sleep_fn(1.5)
        lcd_device.clear()
        return main_loop(
            gpio=gpio,
            lcd_device=lcd_device,
            fetch_data_fn=fetch_data_fn,
            http_client=http_client,
            server_url=server_url,
            sleep_fn=sleep_fn,
            iterations=iterations,
        )
    except KeyboardInterrupt:
        print("종료됨")
        return None
    finally:
        try:
            if lcd_device is not None:
                try:
                    lcd_device.clear()
                finally:
                    lcd_device.destroy()
        finally:
            gpio.cleanup()
