from servo import Servos
from machine import Pin
from machine import I2C
from utime import sleep_ms
import machine
import micropython
import network
import esp
import gc
from umqttsimple import MQTTClient
from machine import I2C
from machine import Pin
from pca9685 import PCA9685
from servo import Servos
import ubinascii
import _thread
import time


def sub_cb(topic, msg):
    global last_topic, last_msg, servos
    print((topic, msg))

    if last_topic == b'RX':
        servos.position(8, abs(int(float(last_msg) * 180)))
    elif last_topic == b'LX':
        servos.position(4, abs(int(float(last_msg) * 180)))

    last_topic = topic
    last_msg = msg

def connect_and_subscribe():
    global client_id, mqtt_server
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_cb)
    client.connect()

    topics = [item for sublist in topics_sub for item in sublist]

    for topic in topics:
        client.subscribe(topic)
        # Delay next topic subscription
        # time.sleep(0.1)

    return client

def walk(ms):
    coaxa = 4
    femur = 7
    patella = 8
    VCC = Pin(15, Pin.OUT)

    VCC.value(1)

    i2c = I2C(0)
    servos = Servos(i2c)
    servos.min_duty = 160
    servos.max_duty = 580

    servos.position(coaxa, degrees=45)
    servos.position(femur, degrees=160)
    servos.position(patella, degrees=90)
    sleep_ms(1000)

    last_com = 0
    counter = 0

    while True:
        try:
            client.check_msg()
            if (time.time() - last_com) > 5:
                # msg = b'Hello #%d' % counter
                # client.publish(topic_pub, msg)
                last_msg = time.time()
                counter += 1
        except OSError as e:
            restart_and_reconnect()

    #last_deg = 45
    for deg in range(45, 136):
        #new_deg = last_deg * 0.7 + deg * 0.3
        servos.position(coaxa, degrees=deg)

        if deg >= 90:
            servos.position(patella, degrees=(45-90+deg))
        else:
            servos.position(patella, degrees=(90 + 45 - deg))

        #last_deg = new_deg
        sleep_ms(ms)

    for deg in range(135, 44, -1):
        #new_deg = last_deg * 0.7 + deg * 0.3
        servos.position(coaxa, degrees=deg)
        #last_deg = new_deg
        sleep_ms(ms)

topic = b""
msg = b""

esp.osdebug(None)
gc.collect()

# Network credentials
ssid = 'HEXDECK'
password = 'fbc275b22e8e'

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

client = None

try:
    client = connect_and_subscribe()
except OSError as e:
    restart_and_reconnect()