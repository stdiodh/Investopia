"""HD44780 16x2 LCD를 4비트 모드로 제어하는 드라이버."""

import time


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
