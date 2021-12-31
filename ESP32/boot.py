import machine
import micropython
import network
import esp
import gc

# Disable OS debug on ESP and enable garbage collection
esp.osdebug(None)
gc.collect()

# Network credentials
ssid = 'TP-LINK_F6B520'
password = ''

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
