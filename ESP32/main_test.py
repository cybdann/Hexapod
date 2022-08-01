from machine import Pin
from machine import I2C
from servo import Servos
from utime import sleep_ms
from hexapod import Hexapod

VCC = Pin(13, Pin.OUT)
CONV = Pin(12, Pin.OUT)

VCC.value(1)
CONV.value(1)

hexa = Hexapod()

rs = Servos(i2c, address=0x40)
ls = Servos(i2c, address=0x41)

while True:
    pass
