from machine import Pin
import machine
import micropython
import network
import esp
import gc

# Enable PWM board and buck converter
VCC = Pin(13, Pin.OUT)
CONV = Pin(12, Pin.OUT)

VCC.value(1)
CONV.value(1)

# Disable OS debug on ESP and enable garbage collection
esp.osdebug(None)
gc.collect()

# Network credentials
ssid = 'URNet'
password = 'urnet1234'

# Create network station
station = network.WLAN(network.STA_IF)

# Reset network connection
if station.isconnected():
    station.disconnect()

station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    pass

print('Connection successful')
print(station.ifconfig())
