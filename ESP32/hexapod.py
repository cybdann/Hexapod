from servo import Servos
from machine import I2C
from machine import Pin
from utime import sleep_ms

from math import degrees
from math import atan2
from math import atan
from math import acos
from math import cos
from math import sin
from math import sqrt

"""
    Hexapod class for the Hexapod robot
    
    PWM boards:
        pwmL -> PWM board for the left side of the body
        pwmR -> PWM board for the right side of the body
        pwm = [pwmL, pwmR]
        
        e.g. pwm[0] selected for the left side
    
    Servo naming conventions:
        Right side of robot -> R
        Left side of robot -> L
        
        Front leg -> 1
        Middle leg -> 2
        Back leg -> 3
        
        Controls Coxa -> C
        Controls Femur -> F
        Controls Tarsus -> T
        
        e.g. L2F servo is found on the left side of the body
        and manipulates the Coxa of the middle leg
        
    Python servo list:
        L1 = [<pwm channel for Coxa>, <pwm channel for Femur>, <pwm channel for Tarsus>]
        .
        .
        .
        R3 = [<pwm channel for Coxa>, <pwm channel for Femur>, <pwm channel for Tarsus>]
        
"""

# Reference leg is always R2
PI = 3.1415

SIN_45 = 0.7071
SIN_135 = 0.7071
SIN_225 = -0.7071
SIN_315 = -0.7071

COS_45 = 0.7071
COS_135 = -0.7071
COS_225 = -0.7071
COS_315 = 0.7071

# Model parameters and constants
d1 = -16.43
a1 = 36.13
a2 = 65.982
a3 = 168.045

# Movement start coordinates
x_start = 127.5
y_start = 127.5  # * sin(offset)
z_start = -160.1

# For locomotion in general (vm, rm, hm, dm)
steps_loc_full = 60
steps_loc_qrt = 15
# For principal axes rotation (roll, pitch, yaw, elevation)
steps_rot = 25

step_angle = PI / steps_loc_full


class Hexapod:

    def __init__(self, i2c=None, gait=b'TR', mode=b'A', sitting=True, esp=False, stopped=False):
        # Set default I2C peripherals if none is provided
        if i2c is None:
            i2c = I2C(1)
        else:
            self.i2c = i2c

        # PWM boards list
        self.ls = Servos(i2c, address=0x41, min_us=1000, max_us=2000)  # Left side
        self.rs = Servos(i2c, address=0x40, min_us=1000, max_us=2000)  # Right side

        # Set max and min duty for servos drivers

        # Servo index list for each leg
        # First index is COXA, second is FEMUR and the last one is TARSUS
        self.L1 = (9, 10, 11)
        self.L2 = (6, 5, 4)
        self.L3 = (2, 1, 0)

        self.R1 = (6, 5, 4)
        self.R2 = (9, 10, 11)
        self.R3 = (13, 14, 15)

        # Servo position list for each leg (Hexapod is powered on while sitting)
        self.L1P = [90, 90, 90]
        self.L2P = [90, 90, 90]
        self.L3P = [90, 90, 90]

        self.R1P = [90, 90, 90]
        self.R2P = [90, 90, 90]
        self.R3P = [90, 90, 90]

        # Servo physical offset in degrees
        self.L1P_offset = (0, -10, -20)
        self.L2P_offset = (-10, -10, -20)
        self.L3P_offset = (-15, 0, -20)

        self.R1P_offset = (0, 10, 30)
        self.R2P_offset = (0, 0, 10)
        self.R3P_offset = (0, 20, 20)

        # Hexapod statuses
        self.gait = gait  # Gait selection (TR = Tripod (default), MT = Metachronal)
        self.mode = mode  # Control mode selection (A = A mode (default), B = B mode)

        self.sitting = sitting  # Is the robot standing?
        self.esp = esp  # Electronic stability control
        self.stopped = stopped  # All servos stopped

        # Locomotion path indexers
        # Tripod
        self.tr_c1 = 1  # First cycle
        self.tr_c2 = 31  # Second cycle

    def test_tripod(self, loop, rx, ry, radius, sleep, locomotion):
        # Example: rx = 0.0 and ry = 1.0 means vertical movement
        # Radius 70
        for _ in range(loop * steps_loc_full):
            self.gait_tripod(locomotion, rx=rx, ry=ry, radius=radius, sleep=sleep)

    def set_status(self, topic, status):
        # SIT/UP button | SS
        if topic[1] == 83:
            self.sitting = not self.sitting
            if status == b'1':
                self.get_up()
            else:
                self.sit_down()
        # ON/OFF ESP | SE
        elif topic[1] == 69:  # Haha, nice
            self.esp = not self.esp
            # TODO: Write ESP algorithm

    def set_mode(self, mode):
        if mode == b'A':
            self.mode = True
        else:
            self.mode = False

    def set_gait(self):
        self.gait = not self.gait

    def get_up(self, ms=30):
        # Set and save COXA servos positions to 90 degrees
        self.L1P[0] = 90
        self.L2P[0] = 90
        self.L3P[0] = 90

        self.R1P[0] = 90
        self.R2P[0] = 90
        self.R3P[0] = 90

        # Set the COXA servos to 90 degrees
        self.ls.position(self.L1[0], degrees=(90 + self.L1P_offset[0]))
        self.rs.position(self.R1[0], degrees=(90 + self.R1P_offset[0]))

        self.ls.position(self.L2[0], degrees=(90 + self.L2P_offset[0]))
        self.rs.position(self.R2[0], degrees=(90 + self.R2P_offset[0]))

        self.ls.position(self.L3[0], degrees=(90 + self.L3P_offset[0]))
        self.rs.position(self.R3[0], degrees=(90 + self.R3P_offset[0]))

        # Get FEMUR and TARSUS to 90 degrees with 5 degrees steps
        for pos in range(0, 50, 5):
            # Set Left side servos to 90 degrees and save last position
            self.L1P[1] = 135 - pos
            self.L2P[1] = 135 - pos
            self.L3P[1] = 135 - pos

            self.L1P[2] = 45 + pos
            self.L2P[2] = 45 + pos
            self.L3P[2] = 45 + pos

            # Set right side servos to 90 degrees and save last position
            self.R1P[1] = 45 + pos
            self.R2P[1] = 45 + pos
            self.R3P[1] = 45 + pos

            self.R1P[2] = 135 - pos
            self.R2P[2] = 135 - pos
            self.R3P[2] = 135 - pos

            # Gradually set legs into default position
            self.ls.position(self.L1[1], degrees=(self.L1P[1] + self.L1P_offset[1]))
            self.rs.position(self.R1[1], degrees=(self.R1P[1] + self.R1P_offset[1]))

            self.ls.position(self.L2[1], degrees=(self.L2P[1] + self.L2P_offset[1]))
            self.rs.position(self.R2[1], degrees=(self.R2P[1] + self.R2P_offset[1]))

            self.ls.position(self.L3[1], degrees=(self.L3P[1] + self.L3P_offset[1]))
            self.rs.position(self.R3[1], degrees=(self.R3P[1] + self.R3P_offset[1]))

            # Gradually set the COXA servos to 90 degrees
            self.ls.position(self.L1[2], degrees=(self.L1P[2] + self.L1P_offset[2]))
            self.rs.position(self.R1[2], degrees=(self.R1P[2] + self.R1P_offset[2]))

            self.ls.position(self.L2[2], degrees=(self.L2P[2] + self.L2P_offset[2]))
            self.rs.position(self.R2[2], degrees=(self.R2P[2] + self.R2P_offset[2]))

            self.ls.position(self.L3[2], degrees=(self.L3P[2] + self.L3P_offset[2]))
            self.rs.position(self.R3[2], degrees=(self.R3P[2] + self.R3P_offset[2]))

            sleep_ms(ms)

    def sit_down(self, ms=30):
        # Set and save COXA servos positions to 90 degrees
        self.L1P[0] = 90
        self.L2P[0] = 90
        self.L3P[0] = 90

        self.R1P[0] = 90
        self.R2P[0] = 90
        self.R3P[0] = 90

        # Set the COXA servos to 90 degrees
        self.ls.position(self.L1[0], degrees=(90 + self.L1P_offset[0]))
        self.rs.position(self.R1[0], degrees=(90 + self.R1P_offset[0]))

        self.ls.position(self.L2[0], degrees=(90 + self.L2P_offset[0]))
        self.rs.position(self.R2[0], degrees=(90 + self.R2P_offset[0]))

        self.ls.position(self.L3[0], degrees=(90 + self.L3P_offset[0]))
        self.rs.position(self.R3[0], degrees=(90 + self.R3P_offset[0]))

        # Get FEMUR and TARSUS to 90 degrees with 5 degrees steps
        for pos in range(0, 50, 5):
            # Set Left side servos to 90 degrees and save last position
            self.L1P[1] = 90 + pos
            self.L2P[1] = 90 + pos
            self.L3P[1] = 90 + pos

            self.L1P[2] = 90 - pos
            self.L2P[2] = 90 - pos
            self.L3P[2] = 90 - pos

            # Set right side servos to 90 degrees and save last position
            self.R1P[1] = 90 - pos
            self.R2P[1] = 90 - pos
            self.R3P[1] = 90 - pos

            self.R1P[2] = 90 + pos
            self.R2P[2] = 90 + pos
            self.R3P[2] = 90 + pos

            # Gradually set legs into default position
            self.ls.position(self.L1[1], degrees=(self.L1P[1] + self.L1P_offset[1]))
            self.rs.position(self.R1[1], degrees=(self.R1P[1] + self.R1P_offset[1]))

            self.ls.position(self.L2[1], degrees=(self.L2P[1] + self.L2P_offset[1]))
            self.rs.position(self.R2[1], degrees=(self.R2P[1] + self.R2P_offset[1]))

            self.ls.position(self.L3[1], degrees=(self.L3P[1] + self.L3P_offset[1]))
            self.rs.position(self.R3[1], degrees=(self.R3P[1] + self.R3P_offset[1]))

            # Gradually set the COXA servos to 90 degrees
            self.ls.position(self.L1[2], degrees=(self.L1P[2] + self.L1P_offset[2]))
            self.rs.position(self.R1[2], degrees=(self.R1P[2] + self.R1P_offset[2]))

            self.ls.position(self.L2[2], degrees=(self.L2P[2] + self.L2P_offset[2]))
            self.rs.position(self.R2[2], degrees=(self.R2P[2] + self.R2P_offset[2]))

            self.ls.position(self.L3[2], degrees=(self.L3P[2] + self.L3P_offset[2]))
            self.rs.position(self.R3[2], degrees=(self.R3P[2] + self.R3P_offset[2]))

            sleep_ms(ms)

    def set_default_position(self):
        # 3 servos on each leg
        for servo in range(3):
            # Set Left side servos to 90 degrees and save last position
            self.L1P[servo] = 90
            self.L2P[servo] = 90
            self.L3P[servo] = 90

            # Set right side servos to 90 degrees and save last position
            self.R1P[servo] = 90
            self.R2P[servo] = 90
            self.R3P[servo] = 90

            # Set legs into default position
            self.ls.position(self.L1[servo], degrees=(self.L1P[servo] + self.L1P_offset[servo]))
            self.rs.position(self.R1[servo], degrees=(self.R1P[servo] + self.R1P_offset[servo]))

            self.ls.position(self.L2[servo], degrees=(self.L2P[servo] + self.L2P_offset[servo]))
            self.rs.position(self.R2[servo], degrees=(self.R2P[servo] + self.R2P_offset[servo]))

            self.ls.position(self.L3[servo], degrees=(self.L3P[servo] + self.L3P_offset[servo]))
            self.rs.position(self.R3[servo], degrees=(self.R3P[servo] + self.R3P_offset[servo]))

    def return_to_default_position(self):
        # Return every servo to 90 degrees
        # This shit is extremely inefficient, but it will do the trick
        flag = True

        while flag:
            # Calculate COXA servo position
            self.R1P[0] = self.R1P[0] if self.R1P[0] == 90 else \
                ((self.R1P[0] - 1) if self.R1P[0] > 90 else (self.R1P[0] + 1))
            self.R2P[0] = self.R2P[0] if self.R2P[0] == 90 else \
                ((self.R2P[0] - 1) if self.R2P[0] > 90 else (self.R2P[0] + 1))
            self.R3P[0] = self.R3P[0] if self.R3P[0] == 90 else \
                ((self.R3P[0] - 1) if self.R3P[0] > 90 else (self.R3P[0] + 1))

            self.L1P[0] = self.L1P[0] if self.L1P[0] == 90 else \
                ((self.L1P[0] - 1) if self.L1P[0] > 90 else (self.L1P[0] + 1))
            self.L2P[0] = self.L2P[0] if self.L2P[0] == 90 else \
                ((self.L2P[0] - 1) if self.L2P[0] > 90 else (self.L2P[0] + 1))
            self.L3P[0] = self.L3P[0] if self.L3P[0] == 90 else \
                ((self.L3P[0] - 1) if self.L3P[0] > 90 else (self.L3P[0] + 1))

            # Check if every servo is at 90 degrees
            if self.R1P[0] == 90 and self.R2P[0] == 90 and self.R3P[0] == 90 and \
                    self.L1P[0] == 90 and self.L2P[0] == 90 and self.L3P[0] == 90:
                flag = False

            # Move COXA
            self.rs.position(self.R1[0], degrees=(self.R1P[0] + self.R1P_offset[0]))
            self.rs.position(self.R2[0], degrees=(self.R2P[0] + self.R2P_offset[0]))
            self.rs.position(self.R3[0], degrees=(self.R3P[0] + self.R3P_offset[0]))

            self.ls.position(self.L1[0], degrees=(self.L1P[0] + self.L1P_offset[0]))
            self.ls.position(self.L2[0], degrees=(self.L2P[0] + self.L2P_offset[0]))
            self.ls.position(self.L3[0], degrees=(self.L3P[0] + self.L3P_offset[0]))

        flag = True

        while flag:
            # Calculate FEMUR servo position
            self.R1P[1] = self.R1P[1] if self.R1P[1] == 90 else \
                ((self.R1P[1] - 1) if self.R1P[1] > 90 else (self.R1P[1] + 1))
            self.R2P[1] = self.R2P[1] if self.R2P[1] == 90 else \
                ((self.R2P[1] - 1) if self.R2P[1] > 90 else (self.R2P[1] + 1))
            self.R3P[1] = self.R3P[1] if self.R3P[1] == 90 else \
                ((self.R3P[1] - 1) if self.R3P[1] > 90 else (self.R3P[1] + 1))

            self.L1P[1] = self.L1P[1] if self.L1P[1] == 90 else \
                ((self.L1P[1] - 1) if self.L1P[1] > 90 else (self.L1P[1] + 1))
            self.L2P[1] = self.L2P[1] if self.L2P[1] == 90 else \
                ((self.L2P[1] - 1) if self.L2P[1] > 90 else (self.L2P[1] + 1))
            self.L3P[1] = self.L3P[1] if self.L3P[1] == 90 else \
                ((self.L3P[1] - 1) if self.L3P[1] > 90 else (self.L3P[1] + 1))

            # Check if every servo is at 90 degrees
            if self.R1P[1] == 90 and self.R2P[1] == 90 and self.R3P[1] == 90 and \
                    self.L1P[1] == 90 and self.L2P[1] == 90 and self.L3P[1] == 90:
                flag = False

            # Move FEMUR
            self.rs.position(self.R1[1], degrees=(self.R1P[1] + self.R1P_offset[1]))
            self.rs.position(self.R2[1], degrees=(self.R2P[1] + self.R2P_offset[1]))
            self.rs.position(self.R3[1], degrees=(self.R3P[1] + self.R3P_offset[1]))

            self.ls.position(self.L1[1], degrees=(self.L1P[1] + self.L1P_offset[1]))
            self.ls.position(self.L2[1], degrees=(self.L2P[1] + self.L2P_offset[1]))
            self.ls.position(self.L3[1], degrees=(self.L3P[1] + self.L3P_offset[1]))

        flag = True

        while flag:
            # Calculate TARSUS servo position
            self.R1P[2] = self.R1P[2] if self.R1P[2] == 90 else \
                ((self.R1P[2] - 1) if self.R1P[2] > 90 else (self.R1P[2] + 1))
            self.R2P[2] = self.R2P[2] if self.R2P[2] == 90 else \
                ((self.R2P[2] - 1) if self.R2P[2] > 90 else (self.R2P[2] + 1))
            self.R3P[2] = self.R3P[2] if self.R3P[2] == 90 else \
                ((self.R3P[2] - 1) if self.R3P[2] > 90 else (self.R3P[2] + 1))

            self.L1P[2] = self.L1P[2] if self.L1P[2] == 90 else \
                ((self.L1P[2] - 1) if self.L1P[2] > 90 else (self.L1P[2] + 1))
            self.L2P[2] = self.L2P[2] if self.L2P[2] == 90 else \
                ((self.L2P[2] - 1) if self.L2P[2] > 90 else (self.L2P[2] + 1))
            self.L3P[2] = self.L3P[2] if self.L3P[2] == 90 else \
                ((self.L3P[2] - 1) if self.L3P[2] > 90 else (self.L3P[2] + 1))

            # Check if every servo is at 90 degrees
            if self.R1P[2] == 90 and self.R2P[2] == 90 and self.R3P[2] == 90 and \
                    self.L1P[2] == 90 and self.L2P[2] == 90 and self.L3P[2] == 90:
                flag = False

            # Move TARSUS
            self.rs.position(self.R1[2], degrees=(self.R1P[2] + self.R1P_offset[2]))
            self.rs.position(self.R2[2], degrees=(self.R2P[2] + self.R2P_offset[2]))
            self.rs.position(self.R3[2], degrees=(self.R3P[2] + self.R3P_offset[2]))

            self.ls.position(self.L1[2], degrees=(self.L1P[2] + self.L1P_offset[2]))
            self.ls.position(self.L2[2], degrees=(self.L2P[2] + self.L2P_offset[2]))
            self.ls.position(self.L3[2], degrees=(self.L3P[2] + self.L3P_offset[2]))

    def gait_tripod(self, locomotion, rx=0.0, ry=0.0, radius=70, sleep=5):
        # In case of wrong value
        try:
            ry = float(ry)
            rx = float(rx)
        except ValueError:
            return

        # Joystick isn't moved or done walk
        if ry == 0.0 and rx == 0.0:
            # Reset indexers and set Hexapod into normal position
            # self.return_to_default_position()
            # self.tr_c1 = 1  # First cycle
            # self.tr_c2 = 31  # Second cycle
            return

        # Calculate rotation angle
        angle = atan2(ry, rx)

        # Second or third quadrant
        if rx < 0.0 and (ry >= 0.0 or ry < 0.0):
            angle += PI
        # Fourth quadrant
        elif rx >= 0.0 and ry < 0.0:
            angle += 2 * PI

        # Get path coordinates
        # Omnidirectional
        if locomotion == "od":
            # Tripod 1st cycle
            path_L1 = self.od_movement([COS_135, SIN_135], angle, radius, self.tr_c1)
            path_R2 = self.od_movement([1, 0], angle, radius, self.tr_c1)
            path_L3 = self.od_movement([COS_225, SIN_225], angle, 50, self.tr_c1)

            # Tripod 2nd cycle
            path_R1 = self.od_movement([COS_45, SIN_45], angle, radius, self.tr_c2)
            path_L2 = self.od_movement([-1, 0], angle, radius, self.tr_c2)
            path_R3 = self.od_movement([COS_315, SIN_315], angle, radius, self.tr_c2)

            # Increment indexer
            self.update_indexer(inc=True)
        # Rotational
        elif locomotion == "rot":
            # Tripod 1st cycle
            path_L1 = self.rotate_movement(PI/4, radius, self.tr_c1)
            path_R2 = self.rotate_movement(0, radius, self.tr_c1)
            path_L3 = self.rotate_movement(-PI/4, radius, self.tr_c1)

            # Tripod 2nd cycle
            path_R1 = self.rotate_movement(3*PI/4, radius, self.tr_c2)
            path_L2 = self.rotate_movement(PI, radius, self.tr_c2)
            path_R3 = self.rotate_movement(5*PI/4, radius, self.tr_c2)

            # Rotating clockwise => increment indexer
            if rx >= 0.0:
                self.update_indexer(inc=True)
            # Rotating counter-clockwise => decrement indexer
            else:
                self.update_indexer(inc=False)

        # Get angles for each leg
        angles_R1 = self.inverse_kinematics(path_R1, [90, -45, -20.5, -100.15], True)
        angles_R2 = self.inverse_kinematics(path_R2, [90, 0, -20.5, -100.15], True)
        angles_R3 = self.inverse_kinematics(path_R3, [90, 45, -20.5, -100.15], True)

        angles_L1 = self.inverse_kinematics(path_L1, [-90, 45, 20.5, 100.15], False)
        angles_L2 = self.inverse_kinematics(path_L2, [-90, 0, 20.5, 100.15], False)
        angles_L3 = self.inverse_kinematics(path_L3, [-90, -45, 20.5, 100.15], False)

        # Save servo angles
        self.L1P = angles_L1
        self.R2P = angles_R2
        self.L3P = angles_L3

        self.R1P = angles_R1
        self.L2P = angles_L2
        self.R3P = angles_R3

        # For debugging
        # print("R1 : " + str(self.R1P))
        # print("R2 : " + str(self.R2P))
        # print("R3 : " + str(self.R3P))
        #
        # print("L1 : " + str(self.L1P))
        # print("L2 : " + str(self.L2P))
        # print("L3 : " + str(self.L3P))

        # 1st cycle
        self.ls.position(self.L1[0], degrees=(self.L1P[0] + self.L1P_offset[0]))
        self.ls.position(self.L1[1], degrees=(self.L1P[1] + self.L1P_offset[1]))
        self.ls.position(self.L1[2], degrees=(self.L1P[2] + self.L1P_offset[2]))

        self.rs.position(self.R2[0], degrees=(self.R2P[0] + self.R2P_offset[0]))
        self.rs.position(self.R2[1], degrees=(self.R2P[1] + self.R2P_offset[1]))
        self.rs.position(self.R2[2], degrees=(self.R2P[2] + self.R2P_offset[2]))

        self.ls.position(self.L3[0], degrees=(self.L3P[0] + self.L3P_offset[0]))
        self.ls.position(self.L3[1], degrees=(self.L3P[1] + self.L3P_offset[1]))
        self.ls.position(self.L3[2], degrees=(self.L3P[2] + self.L3P_offset[2]))

        # 2nd cycle
        self.rs.position(self.R1[0], degrees=(self.R1P[0] + self.R1P_offset[0]))
        self.rs.position(self.R1[1], degrees=(self.R1P[1] + self.R1P_offset[1]))
        self.rs.position(self.R1[2], degrees=(self.R1P[2] + self.R1P_offset[2]))

        self.ls.position(self.L2[0], degrees=(self.L2P[0] + self.L2P_offset[0]))
        self.ls.position(self.L2[1], degrees=(self.L2P[1] + self.L2P_offset[1]))
        self.ls.position(self.L2[2], degrees=(self.L2P[2] + self.L2P_offset[2]))

        self.rs.position(self.R3[0], degrees=(self.R3P[0] + self.R3P_offset[0]))
        self.rs.position(self.R3[1], degrees=(self.R3P[1] + self.R3P_offset[1]))
        self.rs.position(self.R3[2], degrees=(self.R3P[2] + self.R3P_offset[2]))

        # Delay next step
        if sleep is not None:
            sleep_ms(sleep)

    @staticmethod
    def od_movement(offset, rot_angle, radius=50, i=1):
        x = x_start * offset[0]
        y = y_start * offset[1]
        z = z_start

        # Start from apoapsis (180 -> 270 degrees)
        if i < steps_loc_qrt:
            angle = PI / 2 - 2 * i * step_angle

            x = x + i * radius / steps_loc_qrt * cos(rot_angle)
            y = y + i * radius / steps_loc_qrt * sin(rot_angle)
            z = z + radius * sin(angle)
        # Return to ground
        elif i < (steps_loc_full - steps_loc_qrt):
            x = x + (radius - (i - steps_loc_qrt) * radius / steps_loc_qrt) * cos(rot_angle)
            y = y + (radius - (i - steps_loc_qrt) * radius / steps_loc_qrt) * sin(rot_angle)
        # Start again (0 -> 180 degrees)
        else:
            angle = PI - 2 * (i - (steps_loc_full - steps_loc_qrt)) * step_angle

            x = x - (radius - (i - (steps_loc_full - steps_loc_qrt)) * radius / steps_loc_qrt) * cos(rot_angle)
            y = y - (radius - (i - (steps_loc_full - steps_loc_qrt)) * radius / steps_loc_qrt) * sin(rot_angle)
            z = z + radius * sin(angle)

        return [x, y, z]

    @staticmethod
    def rotate_movement(offset, radius=50, i=1):
        x = x_start * cos(offset)
        y = y_start * sin(offset)
        z = z_start

        # Start from apoapsis (180 -> 270 degrees)
        if i < steps_loc_qrt:
            angle = PI / 2 - 2 * i * step_angle

            x = x + radius * sin(angle + offset)
            y = y - radius * cos(angle + offset)
            z = z + radius * sin(angle)
        # Return to ground
        elif i < (steps_loc_full - steps_loc_qrt):
            x = x + (radius - (i - steps_loc_qrt) * radius / steps_loc_qrt) * sin(offset)
            y = y - (radius - (i - steps_loc_qrt) * radius / steps_loc_qrt) * cos(offset)
        # Start again (0 -> 180 degrees)
        else:
            angle = PI - 2 * (i - (steps_loc_full - steps_loc_qrt)) * step_angle

            x = x + radius * sin(angle + offset)
            y = y - radius * cos(angle + offset)
            z = z + radius * sin(angle)

        return [x, y, z]

    @staticmethod
    def inverse_kinematics(coordinates, offset, right_side):
        x = coordinates[0]
        y = coordinates[1]
        z = coordinates[2]

        r1 = sqrt(x * x + y * y)
        r2 = z
        r3 = sqrt((r2 - d1) * (r2 - d1) + (r1 - a1) * (r1 - a1))

        phi1 = atan((r2 - d1) / (r1 - a1))
        phi2 = acos((a3 * a3 - a2 * a2 - r3 * r3) / (-2 * a2 * r3))
        phi3 = acos((r3 * r3 - a2 * a2 - a3 * a3) / (-2 * a2 * a3))

        if x < 0:
            theta_0 = PI + atan(y / x)
        else:
            theta_0 = atan(y / x)

        theta_1 = phi2 + phi1
        theta_2 = PI - phi3

        # Get degrees from radians and offset it with the robot's physical servo position
        theta_0 = degrees(theta_0) + offset[0] + offset[1]

        if right_side:
            theta_1 = degrees(theta_1) + offset[0] + offset[2]
            theta_2 = degrees(theta_2) + offset[0] + offset[3]
        else:
            theta_1 = offset[2] - (degrees(theta_1) + offset[0])
            theta_2 = offset[3] - (degrees(theta_2) + offset[0])

        return [theta_0, theta_1, theta_2]

    def update_indexer(self, inc=True):
        if inc:
            self.tr_c1 += 1
            self.tr_c2 += 1
        else:
            self.tr_c1 -= 1
            self.tr_c2 -= 1

        if self.tr_c1 == steps_loc_full + 1:
            self.tr_c1 = 1
        elif self.tr_c1 == 0:
            self.tr_c1 = steps_loc_full

        if self.tr_c2 == steps_loc_full + 1:
            self.tr_c2 = 1
        elif self.tr_c2 == 0:
            self.tr_c2 = steps_loc_full

    def yaw_rotation(self, lx=0.0, ly=0.0):
        # TODO: Write Hexapod rotation around yaw axis
        pass

    def pitch_rotation(self, rx=0.0, ry=0.0):
        # TODO: Write Hexapod rotation around pitch axis
        pass

    def roll_rotation(self, right):
        # TODO: Write Hexapod rotation around roll axis
        pass