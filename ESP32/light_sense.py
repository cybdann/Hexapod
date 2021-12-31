from umqttsimple import MQTTClient
from pca9685 import PCA9685
from machine import I2C
from machine import Pin
from machine import ADC
from utime import sleep_ms
import ubinascii
import _thread
import time

# MCU MQTT send
send = False
display = True

# MQTT network credentials
mqtt_server = 'broker.hivemq.com'
client_id = ubinascii.hexlify(machine.unique_id())

# MQTT topic subscription and publishing
topics_sub = [b'COMM', b'DISP']


# Display light level with LEDs
def show_light_level(level):
    if level < 1024:
        pwm.duty(index=0, value=(4*level - 1))
        pwm.duty(index=1, value=0)
        pwm.duty(index=2, value=0)
        pwm.duty(index=3, value=0)
    elif 1024 < level < 2048:
        # TODO: Map level value
        pwm.duty(index=0, value=4095)
        pwm.duty(index=1, value=(4*level - 1))
        pwm.duty(index=2, value=0)
        pwm.duty(index=3, value=0)
    elif 2048 < level < 3072:
        # TODO: Map level value
        pwm.duty(index=0, value=4095)
        pwm.duty(index=1, value=4095)
        pwm.duty(index=2, value=(4*level - 1))
        pwm.duty(index=3, value=0)
    else:
        # TODO: Map level value
        pwm.duty(index=0, value=4095)
        pwm.duty(index=1, value=4095)
        pwm.duty(index=2, value=4095)
        pwm.duty(index=3, value=(4*level - 1))


# Hide light level with LEDs
def hide_light_level():
    for i in range(3):
        LED[i].value(0)


# MQTT subscription callback function
def sub_cb(topic, msg):
    global send, display
    print((topic, msg))

    # Check for communication messages
    if topic == b'COMM' and msg == b'1':
        send = True
    elif topic == b'COMM' and msg == b'0':
        send = False

    # Check for display messages:
    if topic == b'DISP' and msg == b'1':
        display = True
    elif topic == b'DISP' and msg == b'0':
        display = False


# Connect and subscribe to MQTT topic
def connect_and_subscribe():
    # MQTT variables
    global client, client_id, mqtt_server
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_cb)
    client.connect()

    # Subscribe to topics
    for topic in topics_sub:
        client.subscribe(topic, qos=0)

    return client


# Machine reset if failed to connect to the MQTT broker
def restart_and_reconnect():
    time.sleep(10)
    machine.reset()


# Connect to MQTT network before looping
client = None

try:
    client = connect_and_subscribe()
except OSError as e:
    restart_and_reconnect()

# Debugging variables
VCC = Pin(14, Pin.OUT)
VCC.value(1)

# Init I2C protocol
i2c = I2C(0, scl=Pin(18), sda=Pin(19))

# Init pwm board
pwm = PCA9685(address=0x41, i2c=i2c)
pwm.freq(freq=60)

LED = [Pin(12, Pin.OUT), Pin(27, Pin.OUT), Pin(25, Pin.OUT)]

# 12 bit analog values
adc = ADC(Pin(32))
adc.atten(ADC.ATTN_11DB)

while True:
    try:
        # Check for incoming MQTT messages
        client.check_msg()

        # Read light level from ADC
        level = adc.read()
        print(level)

        if send:
            # Send to client the light level

            client.publish("LIGHT_LEVEL", str(level))

        if display:
            # Display the light level with LEDs
            show_light_level(level)
        else:
            # Hide light level with LEDs
            hide_light_level()

        # Sample every 10 ms
        sleep_ms(10)

    except OSError as e:
        restart_and_reconnect()
