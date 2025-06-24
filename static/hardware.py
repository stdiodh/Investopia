import RPi.GPIO as GPIO
import time
import pymysql
import requests
from time import sleep
from decimal import Decimal

class LCD:
	# commands
	LCD_CLEARDISPLAY 		= 0x01
	LCD_RETURNHOME 		    = 0x02
	LCD_ENTRYMODESET 		= 0x04
	LCD_DISPLAYCONTROL 		= 0x08
	LCD_CURSORSHIFT 		= 0x10
	LCD_FUNCTIONSET 		= 0x20
	LCD_SETCGRAMADDR 		= 0x40
	LCD_SETDDRAMADDR 		= 0x80

	# flags for display entry mode
	LCD_ENTRYRIGHT 		= 0x00
	LCD_ENTRYLEFT 		= 0x02
	LCD_ENTRYSHIFTINCREMENT 	= 0x01
	LCD_ENTRYSHIFTDECREMENT 	= 0x00

	# flags for display on/off control
	LCD_DISPLAYON 		= 0x04
	LCD_DISPLAYOFF 		= 0x00
	LCD_CURSORON 		= 0x02
	LCD_CURSOROFF 		= 0x00
	LCD_BLINKON 		= 0x01
	LCD_BLINKOFF 		= 0x00

	# flags for display/cursor shift
	LCD_DISPLAYMOVE 	= 0x08
	LCD_CURSORMOVE 		= 0x00

	# flags for display/cursor shift
	LCD_DISPLAYMOVE 	= 0x08
	LCD_CURSORMOVE 		= 0x00
	LCD_MOVERIGHT 		= 0x04
	LCD_MOVELEFT 		= 0x00

	# flags for function set
	LCD_8BITMODE 		= 0x10
	LCD_4BITMODE 		= 0x00
	LCD_2LINE 			= 0x08
	LCD_1LINE 			= 0x00
	LCD_5x10DOTS 		= 0x04
	LCD_5x8DOTS 		= 0x00

	def __init__(self, pin_rs=27, pin_e=22, pins_db=[25, 24, 23, 18], GPIO = None):
		# Emulate the old behavior of using RPi.GPIO if we haven't been given
		# an explicit GPIO interface to use
		if not GPIO:
			import RPi.GPIO as GPIO
			self.GPIO = GPIO
			self.pin_rs = pin_rs
			self.pin_e = pin_e
			self.pins_db = pins_db

			self.used_gpio = self.pins_db[:]
			self.used_gpio.append(pin_e)
			self.used_gpio.append(pin_rs)

			self.GPIO.setwarnings(False)
			self.GPIO.setmode(GPIO.BCM)
			self.GPIO.setup(self.pin_e, GPIO.OUT)
			self.GPIO.setup(self.pin_rs, GPIO.OUT)

			for pin in self.pins_db:
				self.GPIO.setup(pin, GPIO.OUT)

		self.write4bits(0x33) # initialization
		self.write4bits(0x32) # initialization
		self.write4bits(0x28) # 2 line 5x7 matrix
		self.write4bits(0x0C) # turn cursor off 0x0E to enable cursor
		self.write4bits(0x06) # shift cursor right

		self.displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF

		self.displayfunction = self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_5x8DOTS
		self.displayfunction |= self.LCD_2LINE

		""" Initialize to default text direction (for romance languages) """
		self.displaymode =  self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
		self.write4bits(self.LCD_ENTRYMODESET | self.displaymode) #  set the entry mode

		self.clear()

	def begin(self, cols, lines):
		if (lines > 1):
			self.numlines = lines
			self.displayfunction |= self.LCD_2LINE
			self.currline = 0

	def home(self):
		self.write4bits(self.LCD_RETURNHOME) # set cursor position to zero
		self.delayMicroseconds(3000) # this command takes a long time!
	
	def clear(self):
		self.write4bits(self.LCD_CLEARDISPLAY) # command to clear display
		self.delayMicroseconds(3000)	# 3000 microsecond sleep, clearing the display takes a long time

	def setCursor(self, col, row):
		self.row_offsets = [ 0x00, 0x40, 0x14, 0x54 ]

		if ( row > self.numlines ): 
			row = self.numlines - 1 # we count rows starting w/0

		self.write4bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))

	def noDisplay(self): 
		# Turn the display off (quickly)
		self.displaycontrol &= ~self.LCD_DISPLAYON
		self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

	def display(self):
		# Turn the display on (quickly)
		self.displaycontrol |= self.LCD_DISPLAYON
		self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

	def noCursor(self):
		# Turns the underline cursor on/off
		self.displaycontrol &= ~self.LCD_CURSORON
		self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

	def cursor(self):
		# Cursor On
		self.displaycontrol |= self.LCD_CURSORON
		self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

	def noBlink(self):
		# Turn on and off the blinking cursor
		self.displaycontrol &= ~self.LCD_BLINKON
		self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

	def noBlink(self):
		# Turn on and off the blinking cursor
		self.displaycontrol &= ~self.LCD_BLINKON
		self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

	def DisplayLeft(self):
		# These commands scroll the display without changing the RAM
		self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT)

	def scrollDisplayRight(self):
		# These commands scroll the display without changing the RAM
		self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT);

	def leftToRight(self):
		# This is for text that flows Left to Right
		self.displaymode |= self.LCD_ENTRYLEFT
		self.write4bits(self.LCD_ENTRYMODESET | self.displaymode);

	def rightToLeft(self):
		# This is for text that flows Right to Left
		self.displaymode &= ~self.LCD_ENTRYLEFT
		self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

	def autoscroll(self):
		# This will 'right justify' text from the cursor
		self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
		self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

	def noAutoscroll(self): 
		# This will 'left justify' text from the cursor
		self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
		self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

	def write4bits(self, bits, char_mode=False):
		# Send command to LCD
		self.delayMicroseconds(1000) # 1000 microsecond sleep
		bits=bin(bits)[2:].zfill(8)
		self.GPIO.output(self.pin_rs, char_mode)
		for pin in self.pins_db:
			self.GPIO.output(pin, False)
		for i in range(4):
			if bits[i] == "1":
				self.GPIO.output(self.pins_db[::-1][i], True)
		self.pulseEnable()
		for pin in self.pins_db:
			self.GPIO.output(pin, False)
		for i in range(4,8):
			if bits[i] == "1":
				self.GPIO.output(self.pins_db[::-1][i-4], True)
		self.pulseEnable()

	def delayMicroseconds(self, microseconds):
		seconds = microseconds / float(1000000)	# divide microseconds by 1 million for seconds
		sleep(seconds)

	def pulseEnable(self):
		self.GPIO.output(self.pin_e, False)
		self.delayMicroseconds(1)		# 1 microsecond pause - enable pulse must be > 450ns 
		self.GPIO.output(self.pin_e, True)
		self.delayMicroseconds(1)		# 1 microsecond pause - enable pulse must be > 450ns 
		self.GPIO.output(self.pin_e, False)
		self.delayMicroseconds(1)		# commands need > 37us to settle

	def message(self, text):
		# Send string to LCD. Newline wraps to second line
		print ("message: %s"%text)
		for char in text:
			if char == '\n':
				self.write4bits(0xC0) # next line
			else:
				self.write4bits(ord(char),True)
	
	def destroy(self):
		print ("clean up used_gpio")
		self.GPIO.cleanup(self.used_gpio)


# LCD 인스턴스
lcd = LCD()
lcd.begin(16, 2)

# GPIO 핀 정의 및 설정
VRX, VRY, SW = 16, 20, 4
BUTTON_BUY, BUTTON_SELL, BUTTON_BUZZER_OFF = 19, 13, 12
BUZZER, LED_UP, LED_DOWN = 26, 6, 5

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([VRX, VRY], GPIO.IN)
GPIO.setup([SW, BUTTON_BUY, BUTTON_SELL, BUTTON_BUZZER_OFF], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup([BUZZER, LED_UP, LED_DOWN], GPIO.OUT)

SERVER_URL = "http://192.173.0.41:5000"

# DB 연결
def get_connection():
    return pymysql.connect(
        host='192.173.0.41',
        user='root',
        password='qwer1230',
        db='stock_db',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )

# 데이터 로드
def fetch_data():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT symbol, name, last_price, change_rate FROM stock")
    stocks = cur.fetchall()

    cur.execute("SELECT asset FROM user_asset WHERE id=1")
    asset = cur.fetchone()['asset']

    conn.close()
    return stocks, asset

# LCD 표시
def display_stock(stock, asset):
    lcd.clear()
    symbol = stock['symbol'][:6]
    price = f"{stock['last_price']:.1f}"
    rate = f"{stock['change_rate']:+.2f}"
    lcd.setCursor(0, 0)
    lcd.message(f"{symbol:<6} {price:>8}")
    lcd.setCursor(0, 1)
    lcd.message(f"{rate}%  ₩{int(asset):,}")

# LED 표시
def update_total_change_leds(portfolio):
    total_change = sum(float(stock['change_rate'] or 0) for stock in portfolio)

    GPIO.output(LED_UP, total_change > 0)
    GPIO.output(LED_DOWN, total_change < 0)

# 버튼 눌림 체크
def is_pressed(pin):
    return GPIO.input(pin) == GPIO.LOW

# 매수/매도 요청
def send_order(symbol, action):
    try:
        response = requests.post(f"{SERVER_URL}/api/{action}", json={"symbol": symbol, "quantity": 1})
        if response.ok:
            print(f"{action.upper()} 성공: {response.json()['message']}")
        else:
            print(f"{action.upper()} 실패: {response.json().get('message', '오류')}")
    except Exception as e:
        print(f"{action.upper()} 요청 오류: {e}")

# 메인 루프
def main_loop():
    current_index = 0
    while True:
        stocks, asset = fetch_data()
        if not stocks:
            lcd.clear()
            lcd.message("No stock data")
            time.sleep(1)
            continue

        update_total_change_leds(stocks)

        if is_pressed(VRY):  # 아래
            current_index = (current_index + 1) % len(stocks)
            time.sleep(0.3)
        elif is_pressed(VRX):  # 위
            current_index = (current_index - 1) % len(stocks)
            time.sleep(0.3)

        selected_stock = stocks[current_index]
        display_stock(selected_stock, asset)

        if is_pressed(BUTTON_BUY):
            send_order(selected_stock['symbol'], "buy")
            time.sleep(0.3)

        if is_pressed(BUTTON_SELL):
            send_order(selected_stock['symbol'], "sell")
            time.sleep(0.3)

        if is_pressed(BUTTON_BUZZER_OFF):
            GPIO.output(BUZZER, GPIO.LOW)

        time.sleep(0.1)

# 실행
try:
    lcd.clear()
    lcd.message("System Booting...")
    time.sleep(1.5)
    lcd.clear()
    main_loop()
except KeyboardInterrupt:
    print("종료됨")
finally:
    lcd.clear()
    lcd.destroy()
    GPIO.cleanup()

