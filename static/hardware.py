import os
import time

import pymysql
import requests


VRX, VRY, SW = 16, 20, 4
BUTTON_BUY, BUTTON_SELL, BUTTON_BUZZER_OFF = 19, 13, 12
BUZZER, LED_UP, LED_DOWN = 26, 6, 5

SERVER_URL = os.getenv("INVESTOPIA_SERVER_URL", "http://127.0.0.1:5000")
REQUEST_TIMEOUT = 5


class LCD:
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    def __init__(
        self,
        pin_rs=27,
        pin_e=22,
        pins_db=None,
        GPIO=None,
        sleep_fn=time.sleep,
    ):
        if GPIO is None:
            import RPi.GPIO as GPIO

        self.GPIO = GPIO
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = list(pins_db or [25, 24, 23, 18])
        self.used_gpio = [*self.pins_db, pin_e, pin_rs]
        self._sleep = sleep_fn

        self.GPIO.setwarnings(False)
        self.GPIO.setmode(GPIO.BCM)
        self.GPIO.setup(self.pin_e, GPIO.OUT)
        self.GPIO.setup(self.pin_rs, GPIO.OUT)
        for pin in self.pins_db:
            self.GPIO.setup(pin, GPIO.OUT)

        self.write4bits(0x33)
        self.write4bits(0x32)
        self.write4bits(0x28)
        self.write4bits(0x0C)
        self.write4bits(0x06)

        self.displaycontrol = (
            self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        )
        self.displayfunction = (
            self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_5x8DOTS | self.LCD_2LINE
        )
        self.displaymode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)
        self.clear()

    def begin(self, cols, lines):
        if lines > 1:
            self.numlines = lines
            self.displayfunction |= self.LCD_2LINE
            self.currline = 0

    def home(self):
        self.write4bits(self.LCD_RETURNHOME)
        self.delayMicroseconds(3000)

    def clear(self):
        self.write4bits(self.LCD_CLEARDISPLAY)
        self.delayMicroseconds(3000)

    def setCursor(self, col, row):
        self.row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row > self.numlines:
            row = self.numlines - 1
        self.write4bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))

    def noDisplay(self):
        self.displaycontrol &= ~self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def display(self):
        self.displaycontrol |= self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def noCursor(self):
        self.displaycontrol &= ~self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def cursor(self):
        self.displaycontrol |= self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def noBlink(self):
        self.displaycontrol &= ~self.LCD_BLINKON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def DisplayLeft(self):
        self.write4bits(
            self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT
        )

    def scrollDisplayRight(self):
        self.write4bits(
            self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT
        )

    def leftToRight(self):
        self.displaymode |= self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def rightToLeft(self):
        self.displaymode &= ~self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def autoscroll(self):
        self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def noAutoscroll(self):
        self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def write4bits(self, bits, char_mode=False):
        self.delayMicroseconds(1000)
        bits = bin(bits)[2:].zfill(8)
        self.GPIO.output(self.pin_rs, char_mode)
        for pin in self.pins_db:
            self.GPIO.output(pin, False)
        for index in range(4):
            if bits[index] == "1":
                self.GPIO.output(self.pins_db[::-1][index], True)
        self.pulseEnable()
        for pin in self.pins_db:
            self.GPIO.output(pin, False)
        for index in range(4, 8):
            if bits[index] == "1":
                self.GPIO.output(self.pins_db[::-1][index - 4], True)
        self.pulseEnable()

    def delayMicroseconds(self, microseconds):
        self._sleep(microseconds / float(1000000))

    def pulseEnable(self):
        self.GPIO.output(self.pin_e, False)
        self.delayMicroseconds(1)
        self.GPIO.output(self.pin_e, True)
        self.delayMicroseconds(1)
        self.GPIO.output(self.pin_e, False)
        self.delayMicroseconds(1)

    def message(self, text):
        print(f"message: {text}")
        for char in text:
            if char == "\n":
                self.write4bits(0xC0)
            else:
                self.write4bits(ord(char), True)

    def destroy(self):
        print("clean up used_gpio")
        self.GPIO.cleanup(self.used_gpio)


def get_connection():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        db=os.environ["DB_NAME"],
        charset="utf8",
        cursorclass=pymysql.cursors.DictCursor,
    )


def fetch_data(connection_factory=None):
    connection_factory = connection_factory or get_connection
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
