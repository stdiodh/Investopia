import builtins
import importlib
from types import SimpleNamespace

import pytest
import requests

from static import hardware


class FakeGPIO:
    BCM = "BCM"
    IN = "IN"
    OUT = "OUT"
    PUD_UP = "PUD_UP"
    LOW = 0
    HIGH = 1

    def __init__(self):
        self.input_values = {}
        self.mode_calls = []
        self.warning_calls = []
        self.setup_calls = []
        self.output_calls = []
        self.cleanup_calls = []

    def setmode(self, mode):
        self.mode_calls.append(mode)

    def setwarnings(self, enabled):
        self.warning_calls.append(enabled)

    def setup(self, pins, mode, **kwargs):
        self.setup_calls.append((pins, mode, kwargs))

    def input(self, pin):
        return self.input_values.get(pin, self.HIGH)

    def output(self, pin, value):
        self.output_calls.append((pin, value))

    def cleanup(self, pins=None):
        self.cleanup_calls.append(pins)


class FakeLCD:
    def __init__(self):
        self.begin_calls = []
        self.clear_count = 0
        self.cursor_calls = []
        self.messages = []
        self.destroy_count = 0

    def begin(self, columns, lines):
        self.begin_calls.append((columns, lines))

    def clear(self):
        self.clear_count += 1

    def setCursor(self, column, row):
        self.cursor_calls.append((column, row))

    def message(self, text):
        self.messages.append(text)

    def destroy(self):
        self.destroy_count += 1


class FakeHttpClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.post_calls = []

    def post(self, url, **kwargs):
        self.post_calls.append((url, kwargs))
        if self.error is not None:
            raise self.error
        return self.response


class ScriptedCursor:
    def __init__(self, results):
        self.results = iter(results)
        self.executed = []

    def execute(self, sql):
        self.executed.append(sql)

    def fetchall(self):
        return next(self.results)

    def fetchone(self):
        return next(self.results)


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.close_count = 0

    def cursor(self):
        return self._cursor

    def close(self):
        self.close_count += 1


@pytest.fixture
def fake_gpio():
    return FakeGPIO()


@pytest.fixture
def fake_lcd():
    return FakeLCD()


@pytest.fixture
def stocks():
    return [
        {
            "symbol": "005930",
            "name": "Samsung",
            "last_price": 71234,
            "change_rate": 1.25,
        },
        {
            "symbol": "000660",
            "name": "SK Hynix",
            "last_price": 180000,
            "change_rate": -0.75,
        },
    ]


def test_import_does_not_require_rpi_gpio(monkeypatch):
    original_import = builtins.__import__

    def reject_rpi(name, *args, **kwargs):
        if name.startswith("RPi"):
            raise AssertionError("RPi.GPIO must not be imported at module import time")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", reject_rpi)

    importlib.reload(hardware)


def test_lcd_accepts_fake_gpio_without_real_sleep(fake_gpio):
    sleep_calls = []
    lcd = hardware.LCD(GPIO=fake_gpio, sleep_fn=sleep_calls.append)
    lcd.begin(16, 2)

    lcd.message("A\nB")
    lcd.destroy()

    assert fake_gpio.mode_calls == [fake_gpio.BCM]
    assert (27, fake_gpio.OUT, {}) in fake_gpio.setup_calls
    assert (22, fake_gpio.OUT, {}) in fake_gpio.setup_calls
    assert fake_gpio.output_calls
    assert sleep_calls
    assert fake_gpio.cleanup_calls == [[25, 24, 23, 18, 22, 27]]


def test_display_stock_writes_two_lcd_lines(fake_lcd):
    stock = {
        "symbol": "005930-extra",
        "last_price": 71234,
        "change_rate": 1.25,
    }

    hardware.display_stock(stock, 1_000_000, fake_lcd)

    assert fake_lcd.cursor_calls == [(0, 0), (0, 1)]
    assert fake_lcd.messages == [
        "005930  71234.0",
        "+1.25%  ₩1,000,000",
    ]


@pytest.mark.parametrize(
    ("rates", "expected_up", "expected_down"),
    [
        ([1.5, None], True, False),
        ([-1.5, 0.25], False, True),
        ([1.5, -1.5], False, False),
    ],
)
def test_total_change_controls_led_pair(
    fake_gpio, rates, expected_up, expected_down
):
    portfolio = [{"change_rate": rate} for rate in rates]

    hardware.update_total_change_leds(portfolio, fake_gpio)

    assert fake_gpio.output_calls == [
        (hardware.LED_UP, expected_up),
        (hardware.LED_DOWN, expected_down),
    ]


def test_button_is_pressed_only_for_gpio_low(fake_gpio):
    fake_gpio.input_values[hardware.BUTTON_BUY] = fake_gpio.LOW
    fake_gpio.input_values[hardware.BUTTON_SELL] = fake_gpio.HIGH

    assert hardware.is_pressed(hardware.BUTTON_BUY, fake_gpio) is True
    assert hardware.is_pressed(hardware.BUTTON_SELL, fake_gpio) is False


@pytest.mark.parametrize("action", ["buy", "sell"])
def test_send_order_posts_one_share_payload(action, capsys):
    response = SimpleNamespace(ok=True, json=lambda: {"message": "완료"})
    http_client = FakeHttpClient(response=response)

    succeeded = hardware.send_order(
        "005930",
        action,
        http_client=http_client,
        server_url="http://test-server",
    )

    assert succeeded is True
    assert http_client.post_calls == [
        (
            f"http://test-server/api/{action}",
            {
                "json": {"symbol": "005930", "quantity": 1},
                "timeout": hardware.REQUEST_TIMEOUT,
            },
        )
    ]
    timeout = http_client.post_calls[0][1]["timeout"]
    assert isinstance(timeout, (int, float))
    assert timeout > 0
    assert f"{action.upper()} 성공: 완료" in capsys.readouterr().out


def test_send_order_reports_http_error_without_retry(capsys):
    response = SimpleNamespace(ok=False, json=lambda: {"message": "수량 부족"})
    http_client = FakeHttpClient(response=response)

    succeeded = hardware.send_order("005930", "sell", http_client=http_client)

    assert succeeded is False
    assert len(http_client.post_calls) == 1
    assert "SELL 실패: 수량 부족" in capsys.readouterr().out


def test_send_order_reports_connection_failure(capsys):
    http_client = FakeHttpClient(error=requests.ConnectionError("offline"))

    succeeded = hardware.send_order("005930", "buy", http_client=http_client)

    assert succeeded is False
    assert len(http_client.post_calls) == 1
    assert "BUY 요청 오류: offline" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("pressed_pin", "initial_index", "expected_index"),
    [
        (hardware.VRY, 1, 0),
        (hardware.VRX, 0, 1),
    ],
)
def test_stock_navigation_wraps_around(
    fake_gpio,
    fake_lcd,
    stocks,
    pressed_pin,
    initial_index,
    expected_index,
):
    fake_gpio.input_values[pressed_pin] = fake_gpio.LOW
    sleep_calls = []

    current_index = hardware.process_iteration(
        stocks,
        1_000_000,
        initial_index,
        gpio=fake_gpio,
        lcd_device=fake_lcd,
        http_client=FakeHttpClient(),
        sleep_fn=sleep_calls.append,
    )

    assert current_index == expected_index
    assert fake_lcd.messages[0].startswith(stocks[expected_index]["symbol"])
    assert sleep_calls == [0.3, 0.1]


@pytest.mark.parametrize(
    ("button_pin", "action"),
    [
        (hardware.BUTTON_BUY, "buy"),
        (hardware.BUTTON_SELL, "sell"),
    ],
)
def test_order_button_uses_stock_selected_after_navigation(
    fake_gpio, fake_lcd, stocks, button_pin, action
):
    fake_gpio.input_values[hardware.VRY] = fake_gpio.LOW
    fake_gpio.input_values[button_pin] = fake_gpio.LOW
    response = SimpleNamespace(ok=True, json=lambda: {"message": "완료"})
    http_client = FakeHttpClient(response=response)

    current_index = hardware.process_iteration(
        stocks,
        1_000_000,
        0,
        gpio=fake_gpio,
        lcd_device=fake_lcd,
        http_client=http_client,
        server_url="http://test-server",
        sleep_fn=lambda seconds: None,
    )

    assert current_index == 1
    assert http_client.post_calls[0] == (
        f"http://test-server/api/{action}",
        {
            "json": {"symbol": "000660", "quantity": 1},
            "timeout": hardware.REQUEST_TIMEOUT,
        },
    )


def test_buzzer_off_button_writes_low(fake_gpio, fake_lcd, stocks):
    fake_gpio.input_values[hardware.BUTTON_BUZZER_OFF] = fake_gpio.LOW

    hardware.process_iteration(
        stocks,
        1_000_000,
        0,
        gpio=fake_gpio,
        lcd_device=fake_lcd,
        sleep_fn=lambda seconds: None,
    )

    assert (hardware.BUZZER, fake_gpio.LOW) in fake_gpio.output_calls


def test_fetch_data_uses_fake_database_and_closes_connection(stocks):
    cursor = ScriptedCursor([stocks, {"asset": 500_000}])
    connection = FakeConnection(cursor)

    result = hardware.fetch_data(connection_factory=lambda: connection)

    assert result == (stocks, 500_000)
    assert "FROM stock" in cursor.executed[0]
    assert "FROM user_asset" in cursor.executed[1]
    assert connection.close_count == 1


def test_bounded_main_loop_handles_empty_stock_list_without_real_sleep(
    fake_gpio, fake_lcd
):
    sleep_calls = []

    current_index = hardware.main_loop(
        gpio=fake_gpio,
        lcd_device=fake_lcd,
        fetch_data_fn=lambda: ([], 0),
        sleep_fn=sleep_calls.append,
        iterations=1,
    )

    assert current_index == 0
    assert fake_lcd.messages == ["No stock data"]
    assert sleep_calls == [1]


def test_run_initializes_devices_and_always_cleans_up(
    fake_gpio, fake_lcd, stocks
):
    sleep_calls = []

    result = hardware.run(
        gpio=fake_gpio,
        lcd_factory=lambda **kwargs: fake_lcd,
        fetch_data_fn=lambda: (stocks, 1_000_000),
        http_client=FakeHttpClient(),
        sleep_fn=sleep_calls.append,
        iterations=1,
    )

    assert result == 0
    assert fake_gpio.mode_calls == [fake_gpio.BCM]
    assert fake_lcd.begin_calls == [(16, 2)]
    assert fake_lcd.messages[0] == "System Booting..."
    assert fake_lcd.destroy_count == 1
    assert fake_gpio.cleanup_calls == [None]
    assert sleep_calls == [1.5, 0.1]


def test_run_cleans_up_after_keyboard_interrupt(fake_gpio, fake_lcd, capsys):
    def interrupt():
        raise KeyboardInterrupt

    result = hardware.run(
        gpio=fake_gpio,
        lcd_factory=lambda **kwargs: fake_lcd,
        fetch_data_fn=interrupt,
        sleep_fn=lambda seconds: None,
        iterations=1,
    )

    assert result is None
    assert fake_lcd.destroy_count == 1
    assert fake_gpio.cleanup_calls == [None]
    assert "종료됨" in capsys.readouterr().out


def test_run_still_destroys_devices_when_final_lcd_clear_fails(
    fake_gpio, fake_lcd
):
    def interrupt():
        raise KeyboardInterrupt

    def fail_on_final_clear():
        fake_lcd.clear_count += 1
        if fake_lcd.clear_count == 3:
            raise RuntimeError("LCD clear failed")

    fake_lcd.clear = fail_on_final_clear

    with pytest.raises(RuntimeError, match="LCD clear failed"):
        hardware.run(
            gpio=fake_gpio,
            lcd_factory=lambda **kwargs: fake_lcd,
            fetch_data_fn=interrupt,
            sleep_fn=lambda seconds: None,
            iterations=1,
        )

    assert fake_lcd.destroy_count == 1
    assert fake_gpio.cleanup_calls == [None]


def test_run_still_cleans_gpio_when_lcd_destroy_fails(fake_gpio, fake_lcd):
    def interrupt():
        raise KeyboardInterrupt

    def fail_destroy():
        fake_lcd.destroy_count += 1
        raise RuntimeError("LCD destroy failed")

    fake_lcd.destroy = fail_destroy

    with pytest.raises(RuntimeError, match="LCD destroy failed"):
        hardware.run(
            gpio=fake_gpio,
            lcd_factory=lambda **kwargs: fake_lcd,
            fetch_data_fn=interrupt,
            sleep_fn=lambda seconds: None,
            iterations=1,
        )

    assert fake_lcd.destroy_count == 1
    assert fake_gpio.cleanup_calls == [None]
