from locomotion import Locomotion
from umqttsimple import MQTTClient
from machine import I2C
from machine import Pin
from pca9685 import PCA9685
from servo import Servos
import ubinascii
import _thread
import time
from utime import sleep_ms

# MQTT network credentials
mqtt_server = '192.168.1.101'
client_id = ubinascii.hexlify(machine.unique_id())

# MQTT topic subscription and publishing
joysticks = [b'R', b'L']
dPads = [b'DU', b'DR', b'DL', b'DD']
face_buttons = [b'MODE', b'GAIT']
statuses = [b'SM', b'SE', b'SS']
topics_sub = [joysticks, dPads, face_buttons, statuses]

# MQTT variables
last_topic = None
last_msg = None

# MQTT subscription callback function
def sub_cb(topic, msg):
    # Joystick data is transmitted in R||L = 'x,y' format (comma separated)
    global Hexapod
    print((topic, msg))

    # Check for mode selection
    if topic == b'MODE':
        Hexapod.mode = msg
        return

    # Check for gait selection
    if topic == b'GAIT':
        Hexapod.gait = msg
        return

    # Control Mode A is selected
    if Hexapod.mode == b'A':
        # Check for right joystick axis and tripod gait
        if topic == b'R' and Hexapod.gait == b'TR':
            if msg[3] == 44:
                Hexapod.tripod(rx=msg[:3], ry=msg[4:])
            else:
                Hexapod.tripod(rx=msg[:4], ry=msg[5:])
        # Check for right joystick axis and metachronal gait
        elif topic == b'R' and Hexapod.gait == b'MT':
            if msg[3] == 44:
                Hexapod.metachronal(rx=msg[:3], ry=msg[4:])
            else:
                Hexapod.metachronal(rx=msg[:4], ry=msg[5:])

        # Check for left joystick axis
        elif topic == b'L':
            # TODO: Yaw rotation (NOT COMPLETED)
            if msg[3] == 44:
                Hexapod.yaw_rotation(lx=msg[:3], ly=msg[4:])
            else:
                Hexapod.yaw_rotation(lx=msg[:4], ly=msg[5:])
            pass
    # Control Mode B is selected
    elif Hexapod.mode == b'B':
        # Raise Hexapod body height
        if topic == b'DU':
            Hexapod.body_elevation(rise=True)
        # Lower Hexapod body height
        elif topic == b'DD':
            Hexapod.body_elevation(rise=False)
        # Roll Hexapod body to the right
        elif topic == b'DR':
            # TODO: Roll rotation (NOT COMPLETED)
            Hexapod.roll_rotation(right=True)
        # Roll Hexapod body to the left
        elif topic == b'DL':
            # TODO: Roll rotation (NOT COMPLETED)
            Hexapod.roll_rotation(right=False)
    # Check for incoming status messages
    else:
        pass


# Connect and subscribe to MQTT topic
def connect_and_subscribe():
    # MQTT variables
    global client, client_id, mqtt_server
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_cb)
    client.connect(clean_session=True)

    # Topics list to subscribe to
    topics = [item for sublist in topics_sub for item in sublist]

    # Subscribe to topics
    for topic in topics:
        client.subscribe(topic, qos=0)

    return client


# Machine reset if failed to connect to the MQTT broker
def restart_and_reconnect():
    time.sleep(10)
    machine.reset()


# Debugging variables
Pin(15, Pin.OUT).value(1)   # Power PCA9685

# Hexapod control
Hexapod = Locomotion()
Hexapod.set_default_position()

# Connect to MQTT network before looping
client = None

try:
    client = connect_and_subscribe()
except OSError as e:
    restart_and_reconnect()

# MCU main thread (Core 1)
while True:
    try:
        client.check_msg()
    except OSError as e:
        restart_and_reconnect()
