from hexapod import Hexapod
from umqttsimple import MQTTClient
from machine import I2C
from machine import Pin
from pca9685 import PCA9685
from servo import Servos
import ubinascii
import _thread
import time
from utime import sleep_ms


# MCU robot control thread (Core 2)
# Used for continuous movement
def control_thread():
    global Hexapod, last_msg, last_topic

    while True:
        # Control Mode A is selected
        if Hexapod.mode == b'A':
            # Check for right joystick axis and tripod gait
            if last_topic == b'R' and Hexapod.gait == b'TR':
                if last_msg[3] == 44:
                    Hexapod.gait_tripod("od", last_msg[:3], last_msg[4:], 70, None)
                else:
                    Hexapod.gait_tripod("od", last_msg[:4], last_msg[5:], 70, None)
            # Check for right joystick axis and metachronal gait
            elif last_topic == b'R' and Hexapod.gait == b'MT':
                if msg[3] == 44:
                    Hexapod.gait_metachronal(rx=last_msg[:3], ry=last_msg[4:])
                else:
                    Hexapod.gait_metachronal(rx=last_msg[:4], ry=last_msg[5:])

            # Check for left joystick axis
            elif last_topic == b'L':
                print(last_msg)
                if last_msg[3] == 44:
                    Hexapod.gait_tripod("rot", last_msg[:3], last_msg[4:], 50, None)
                else:
                    Hexapod.gait_tripod("rot", last_msg[:4], last_msg[5:], 50, None)
                pass


# MQTT subscription callback function
# Used for precision movement
def sub_cb(topic, msg):
    # Joystick data is transmitted in R||L = 'x,y' format (comma separated)
    global Hexapod, last_msg, last_topic

    # Transmit variable to second thread
    # Save msg first, so that it won't run into non-number errors
    last_msg = msg
    last_topic = topic

    # Check for mode selection
    if topic == b'MODE':
        Hexapod.mode = msg
        print("Mode: " + str(msg))
        return

    # Check for gait selection
    if topic == b'GAIT':
        Hexapod.gait = msg
        print("Gait: " + str(msg))
        return

    # Check for incoming status messages
    if topic[0] == 83:
        print(str(topic) + ": " + str(msg))

        # SHUTDOWN Hexapod
        if topic[1] == 77:
            client.publish("SX", "0", retain=True)
            CONV.value(0)
            VCC.value(0)
            return

        Hexapod.set_status(topic, msg)
        client.publish("SX", "1", retain=True)
        return

    # Control Mode A is selected
    if Hexapod.mode == b'A':
        # Vertical movement, forwards
        if last_topic == b'DU':
            Hexapod.gait_tripod("od", 0.0, 1.0, 70, None)
        # Vertical movement, backwards
        elif last_topic == b'DD':
            Hexapod.gait_tripod("od", 0.0, -1.0, 70, None)
        # Horizontal movement,
        elif last_topic == b'DR':
            Hexapod.gait_tripod("od", 1.0, 0.0, 70, None)
        # Roll Hexapod body to the left
        elif last_topic == b'DL':
            Hexapod.gait_tripod("od", -1.0, 0.0, 70, None)
    # Control Mode B is selected
    elif Hexapod.mode == b'B':
        # Raise Hexapod body height
        if last_topic == b'DU':
            Hexapod.body_elevation(rise=True)
        # Lower Hexapod body height
        elif last_topic == b'DD':
            Hexapod.body_elevation(rise=False)
        # Roll Hexapod body to the right
        elif last_topic == b'DR':
            # TODO: Roll rotation (NOT COMPLETED)
            Hexapod.roll_rotation(right=True)
        # Roll Hexapod body to the left
        elif last_topic == b'DL':
            # TODO: Roll rotation (NOT COMPLETED)
            Hexapod.roll_rotation(right=False)


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


# MQTT network credentials
mqtt_server = '172.16.0.104'
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

# Hexapod control
Hexapod = Hexapod()

# Enable PWM board and buck converter
VCC = Pin(13, Pin.OUT)
CONV = Pin(12, Pin.OUT)

# Connect to MQTT network before looping
client = None

try:
    client = connect_and_subscribe()
    print("MQTT client connection successful")
except OSError as e:
    restart_and_reconnect()
    print("MQTT client connection unsuccessful")

# Send Hexapod READY msg to broker
client.publish("SX", "1", retain=True)

# Init robot control thread (Core 2)
c_thread = _thread.start_new_thread(control_thread, ())

# MCU main thread (Core 1)
while True:
    try:
        client.check_msg()
    except OSError as e:
        restart_and_reconnect()
