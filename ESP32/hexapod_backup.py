from servo import Servos
from machine import I2C
from utime import sleep_ms
from math import ceil
import gaits

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


# Roll movement tuple indexer
def rot_ind(up, i):
    if up:
        i += 1
    else:
        i -= 1

    if i == -1:
        i = 0
    elif i == Hexapod.path_samples_2:
        i = 49

    return i


# Locomotion movement tuple indexer
def loc_ind(up, i):
    if up:
        i += 1
    else:
        i -= 1

    if i == -1:
        i = Hexapod.path_samples_1 - 1
    elif loc_ind.i == Hexapod.path_samples_1:
        i = 0

    return i


class Hexapod:
    # Samples in tuples for paths
    # For locomotion in general (vm, rm, hm, dm)
    path_samples_1 = 50
    # For principal axes rotation (roll, pitch, yaw, elevation)
    path_samples_2 = 25

    def __init__(self, i2c=None, gait=b'TR', mode=b'A', walk=False, esp=False, stopped=False):
        # Set default I2C peripherals if none is provided
        if i2c is None:
            i2c = I2C(0)
        else:
            self.i2c = i2c

        # PWM boards list
        self.ls = Servos(i2c, address=0x41)  # Left side
        self.rs = Servos(i2c, address=0x40)  # Right side

        # Set max and min duty for servos drivers
        # FOR THE LOVE OF GOD, LEAVE THIS AS IT IS, UNLESS YOU WANT BURNT DOWN SERVOS
        self.rs.max_duty = 580
        self.ls.max_duty = 580

        self.rs.min_duty = 160
        self.ls.min_duty = 160

        # Servo index list for each leg
        # First index is COXA, second is FEMUR and the last one is TARSUS
        self.L1 = (9, 10, 11)
        self.L2 = (5, 6, 7)
        self.L3 = (2, 1, 0)

        self.R1 = (6, 5, 4)
        self.R2 = (10, 9, 8)
        self.R3 = (13, 14, 15)

        # Servo position list for each leg (Hexapod is powered on while sitting)
        self.L1P = [90, 90, 90]
        self.L2P = [90, 90, 90]
        self.L3P = [90, 90, 90]

        self.R1P = [90, 90, 90]
        self.R2P = [90, 90, 90]
        self.R3P = [90, 90, 90]

        # Servo physical offset in degrees
        self.L1P_offset = (0, 10, -10)
        self.L2P_offset = (5, 10, -10)
        self.L3P_offset = (5, 10, -10)

        self.R1P_offset = (10, -20, -10)
        self.R2P_offset = (0, 25, -10)
        self.R3P_offset = (-10, -30, 0)

        # Hexapod statuses
        self.gait = gait  # Gait selection (TR = Tripod (default), MT = Metachronal)
        self.mode = mode  # Control mode selection (A = A mode (default), B = B mode)

        self.walk = walk  # Is the robot standing?
        self.esp = esp  # Electronic stability control
        self.stopped = stopped  # All servos stopped

        # Locomotion indexer
        # Tripod cycle indexers
        self.trc1_ind = 0
        self.trc2_ind = ceil(self.path_samples_1 / 2)

        # Metachronal cycle indexers
        self.mtc1_ind = 0
        self.mtc2_ind = ceil(self.path_samples_1 / 2)

        # Rotation indexer
        self.rt_ind = ceil(self.path_samples_2 / 2)

    def set_status(self, status):
        # SIT/UP button
        if status[1] == 87:
            self.walk = not self.walk
            # TODO: self.sit_down OR self.get_up
        # STOP/START all servos
        elif status[1] == 83:
            self.stopped = not self.stopped
            # TODO: STOP/START every servo motor on Hexapod
        # ON/OFF ESP
        elif status[1] == 69:  # Haha, nice
            self.esp = not self.esp
            # TODO: Write ESP algorithm

    def set_mode(self, mode):
        if mode == b'A':
            self.mode = True
        else:
            self.mode = False

    def set_gait(self):
        self.gait = not self.gait

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

            # Move left side servos
            self.ls.position(self.L1[servo], degrees=(self.L1P[servo] + self.L1P_offset[servo]))
            self.ls.position(self.L2[servo], degrees=(self.L2P[servo] + self.L2P_offset[servo]))
            self.ls.position(self.L3[servo], degrees=(self.L3P[servo] + self.L3P_offset[servo]))

            # Move right  side servos
            self.rs.position(self.R1[servo], degrees=(self.R1P[servo] + self.R1P_offset[servo]))
            self.rs.position(self.R2[servo], degrees=(self.R2P[servo] + self.R2P_offset[servo]))
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

            # Move COXA
            self.rs.position(self.R1[0], degrees=(self.R1P[0] + self.R1P_offset[0]))
            self.rs.position(self.R2[0], degrees=(self.R2P[0] + self.R2P_offset[0]))
            self.rs.position(self.R3[0], degrees=(self.R3P[0] + self.R3P_offset[0]))

            self.ls.position(self.L1[0], degrees=(self.L1P[0] + self.L1P_offset[0]))
            self.ls.position(self.L2[0], degrees=(self.L2P[0] + self.L2P_offset[0]))
            self.ls.position(self.L3[0], degrees=(self.L3P[0] + self.L3P_offset[0]))

            # Delay for next increment
            sleep_ms(2)

            # Check if every servo is at 90 degrees
            if self.R1P[0] == 90 and self.R2P[0] == 90 and self.R3P[0] == 90 and \
                    self.L1P[0] == 90 and self.L2P[0] == 90 and self.L3P[0] == 90:
                flag = False

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

            # Move FEMUR
            self.rs.position(self.R1[1], degrees=(self.R1P[1] + self.R1P_offset[1]))
            self.rs.position(self.R2[1], degrees=(self.R2P[1] + self.R2P_offset[1]))
            self.rs.position(self.R3[1], degrees=(self.R3P[1] + self.R3P_offset[1]))

            self.ls.position(self.L1[1], degrees=(self.L1P[1] + self.L1P_offset[1]))
            self.ls.position(self.L2[1], degrees=(self.L2P[1] + self.L2P_offset[1]))
            self.ls.position(self.L3[1], degrees=(self.L3P[1] + self.L3P_offset[1]))

            # Delay for next increment
            sleep_ms(2)

            # Check if every servo is at 90 degrees
            if self.R1P[1] == 90 and self.R2P[1] == 90 and self.R3P[1] == 90 and \
                    self.L1P[1] == 90 and self.L2P[1] == 90 and self.L3P[1] == 90:
                flag = False

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

            # Move TARSUS
            self.rs.position(self.R1[2], degrees=(self.R1P[2] + self.R1P_offset[2]))
            self.rs.position(self.R2[2], degrees=(self.R2P[2] + self.R2P_offset[2]))
            self.rs.position(self.R3[2], degrees=(self.R3P[2] + self.R3P_offset[2]))

            self.ls.position(self.L1[2], degrees=(self.L1P[2] + self.L1P_offset[2]))
            self.ls.position(self.L2[2], degrees=(self.L2P[2] + self.L2P_offset[2]))
            self.ls.position(self.L3[2], degrees=(self.L3P[2] + self.L3P_offset[2]))

            # Delay for next increment
            sleep_ms(2)

            # Check if every servo is at 90 degrees
            if self.R1P[2] == 90 and self.R2P[2] == 90 and self.R3P[2] == 90 and \
                    self.L1P[2] == 90 and self.L2P[2] == 90 and self.L3P[2] == 90:
                flag = False

    def gait_tripod(self, rx=0, ry=0):
        # Delay percentage got from joystick
        try:
            dry = float(ry)
            drx = float(rx)
        except ValueError:
            return

        # Joystick isn't moved or done walk
        if dry == 0.0 and drx == 0.0:
            # Reset indexers and set Hexapod into normal position
            self.trc1_ind = 0
            self.trc2_ind = ceil(len(gaits.vm_R1C) / 2)
            self.set_default_position()
            return

        # Check for walking direction for each axis
        dir_ry = True if dry >= 0.0 else False  # True is forward, False is backwards
        dir_rx = True if drx >= 0.0 else False  # True is right, False is left

        # Determine movement type
        if abs(dry) < 0.5 and abs(drx) < 0.5:
            if abs(dry) >= abs(drx):
                # Vertical movement
                self.vertical_movement(abs(dry), dir_ry)
            else:
                self.horizontal_movement(abs(drx), dir_rx)
                # Horizontal movement
        elif abs(dry) >= 0.5 > abs(drx):
            # Vertical movement
            self.vertical_movement(abs(dry), dir_ry)
        elif abs(dry) < 0.5 <= abs(drx):
            # Horizontal movement
            self.horizontal_movement(abs(drx), dir_rx)
        elif dry >= 0 and drx >= 0 or dry < 0 and drx < 0:
            # Diagonal right movement
            self.diagonal_right_movement(drx, dry, (True if (dry and drx) >= 0.0 else False))
        elif dry >= 0 > drx or dry < 0 <= drx:
            # Diagonal right movement
            self.diagonal_left_movement(drx, dry, (True if (dry >= 0 and drx < 0) else False))

    def gait_metachronal(self, rx=0, ry=0):
        # TODO: Write Hexapod Metachronal movement
        pass

    def vertical_movement(self, dry, inc):
        # Cycle 1
        # L1
        self.ls.position(self.L1[0], degrees=(gaits.vm_L1C[self.trc1_ind] + self.L1P_offset[0]))
        self.ls.position(self.L1[1], degrees=(gaits.vm_L1F[self.trc1_ind] + self.L1P_offset[1]))
        self.ls.position(self.L1[2], degrees=(gaits.vm_L1T[self.trc1_ind] + self.L1P_offset[2]))

        # Save positions
        self.L1P[0] = gaits.vm_L1C[self.trc1_ind]
        self.L1P[1] = gaits.vm_L1F[self.trc1_ind]
        self.L1P[2] = gaits.vm_L1T[self.trc1_ind]

        # L3
        self.ls.position(self.L3[0], degrees=(gaits.vm_L3C[self.trc1_ind] + self.L3P_offset[0]))
        self.ls.position(self.L3[1], degrees=(gaits.vm_L3F[self.trc1_ind] + self.L3P_offset[1]))
        self.ls.position(self.L3[2], degrees=(gaits.vm_L3T[self.trc1_ind] + self.L3P_offset[2]))

        # Save positions
        self.L3P[0] = gaits.vm_L3C[self.trc1_ind]
        self.L3P[1] = gaits.vm_L3F[self.trc1_ind]
        self.L3P[2] = gaits.vm_L3T[self.trc1_ind]

        # R2
        self.rs.position(self.R2[0], degrees=(gaits.vm_R2C[self.trc1_ind] + self.R2P_offset[0]))
        self.rs.position(self.R2[1], degrees=(gaits.vm_R2F[self.trc1_ind] + self.R2P_offset[1]))
        self.rs.position(self.R2[2], degrees=(gaits.vm_R2T[self.trc1_ind] + self.R2P_offset[2]))

        # Save positions
        self.R2P[0] = gaits.vm_R2C[self.trc1_ind]
        self.R2P[1] = gaits.vm_R2F[self.trc1_ind]
        self.R2P[2] = gaits.vm_R2T[self.trc1_ind]

        # Cycle 2
        # R1
        self.rs.position(self.R1[0], degrees=(gaits.vm_R1C[self.trc2_ind] + self.R1P_offset[0]))
        self.rs.position(self.R1[1], degrees=(gaits.vm_R1F[self.trc2_ind] + self.R1P_offset[1]))
        self.rs.position(self.R1[2], degrees=(gaits.vm_R1T[self.trc2_ind] + self.R1P_offset[2]))

        # Save positions
        self.R1P[0] = gaits.vm_R1C[self.trc2_ind]
        self.R1P[1] = gaits.vm_R1F[self.trc2_ind]
        self.R1P[2] = gaits.vm_R1T[self.trc2_ind]

        # R3
        self.rs.position(self.R3[0], degrees=(gaits.vm_R3C[self.trc2_ind] + self.R3P_offset[0]))
        self.rs.position(self.R3[1], degrees=(gaits.vm_R3F[self.trc2_ind] + self.R3P_offset[1]))
        self.rs.position(self.R3[2], degrees=(gaits.vm_R3T[self.trc2_ind] + self.R3P_offset[2]))

        # Save positions
        self.R3P[0] = gaits.vm_R3C[self.trc2_ind]
        self.R3P[1] = gaits.vm_R3F[self.trc2_ind]
        self.R3P[2] = gaits.vm_R3T[self.trc2_ind]

        # L2
        self.ls.position(self.L2[0], degrees=(gaits.vm_L2C[self.trc2_ind] + self.L2P_offset[0]))
        self.ls.position(self.L2[1], degrees=(gaits.vm_L2F[self.trc2_ind] + self.L2P_offset[1]))
        self.ls.position(self.L2[2], degrees=(gaits.vm_L2T[self.trc2_ind] + self.L2P_offset[2]))

        # Save positions
        self.L2P[0] = gaits.vm_L2C[self.trc2_ind]
        self.L2P[1] = gaits.vm_L2F[self.trc2_ind]
        self.L2P[2] = gaits.vm_L2T[self.trc2_ind]

        self.trc1_ind = loc_ind(inc, self.trc1_ind)
        self.trc2_ind = loc_ind(inc, self.trc2_ind)

        # Delay between gait cycles with speed factor got from joystick
        sleep_ms(int(5 * (2.0 - dry)))

    def horizontal_movement(self, drx, inc):
        # Cycle 1
        # L1
        self.ls.position(self.L1[0], degrees=(gaits.hm_L1C[self.trc1_ind] + self.L1P_offset[0]))
        self.ls.position(self.L1[1], degrees=(gaits.hm_L1F[self.trc1_ind] + self.L1P_offset[1]))
        self.ls.position(self.L1[2], degrees=(gaits.hm_L1T[self.trc1_ind] + self.L1P_offset[2]))

        # Save positions
        self.L1P[0] = gaits.hm_L1C[self.trc1_ind]
        self.L1P[1] = gaits.hm_L1F[self.trc1_ind]
        self.L1P[2] = gaits.hm_L1T[self.trc1_ind]

        # L3
        self.ls.position(self.L3[0], degrees=(gaits.hm_L3C[self.trc1_ind] + self.L3P_offset[0]))
        self.ls.position(self.L3[1], degrees=(gaits.hm_L3F[self.trc1_ind] + self.L3P_offset[1]))
        self.ls.position(self.L3[2], degrees=(gaits.hm_L3T[self.trc1_ind] + self.L3P_offset[2]))

        # Save positions
        self.L3P[0] = gaits.hm_L3C[self.trc1_ind]
        self.L3P[1] = gaits.hm_L3F[self.trc1_ind]
        self.L3P[2] = gaits.hm_L3T[self.trc1_ind]

        # R2
        self.rs.position(self.R2[0], degrees=(gaits.hm_R2C[self.trc1_ind] + self.R2P_offset[0]))
        self.rs.position(self.R2[1], degrees=(gaits.hm_R2F[self.trc1_ind] + self.R2P_offset[1]))
        self.rs.position(self.R2[2], degrees=(gaits.hm_R2T[self.trc1_ind] + self.R2P_offset[2]))

        # Save positions
        self.R2P[0] = gaits.hm_R2C[self.trc1_ind]
        self.R2P[1] = gaits.hm_R2F[self.trc1_ind]
        self.R2P[2] = gaits.hm_R2T[self.trc1_ind]

        # Cycle 2
        # R1
        self.rs.position(self.R1[0], degrees=(gaits.hm_R1C[self.trc2_ind] + self.R1P_offset[0]))
        self.rs.position(self.R1[1], degrees=(gaits.hm_R1F[self.trc2_ind] + self.R1P_offset[1]))
        self.rs.position(self.R1[2], degrees=(gaits.hm_R1T[self.trc2_ind] + self.R1P_offset[2]))

        # Save positions
        self.R1P[0] = gaits.hm_R1C[self.trc2_ind]
        self.R1P[1] = gaits.hm_R1F[self.trc2_ind]
        self.R1P[2] = gaits.hm_R1T[self.trc2_ind]

        # R3
        self.rs.position(self.R3[0], degrees=(gaits.hm_R3C[self.trc2_ind] + self.R3P_offset[0]))
        self.rs.position(self.R3[1], degrees=(gaits.hm_R3F[self.trc2_ind] + self.R3P_offset[1]))
        self.rs.position(self.R3[2], degrees=(gaits.hm_R3T[self.trc2_ind] + self.R3P_offset[2]))

        # Save positions
        self.R3P[0] = gaits.hm_R3C[self.trc2_ind]
        self.R3P[1] = gaits.hm_R3F[self.trc2_ind]
        self.R3P[2] = gaits.hm_R3T[self.trc2_ind]

        # L2
        self.ls.position(self.L2[0], degrees=(gaits.hm_L2C[self.trc2_ind] + self.L2P_offset[0]))
        self.ls.position(self.L2[1], degrees=(gaits.hm_L2F[self.trc2_ind] + self.L2P_offset[1]))
        self.ls.position(self.L2[2], degrees=(gaits.hm_L2T[self.trc2_ind] + self.L2P_offset[2]))

        # Save positions
        self.L2P[0] = gaits.hm_L2C[self.trc2_ind]
        self.L2P[1] = gaits.hm_L2F[self.trc2_ind]
        self.L2P[2] = gaits.hm_L2T[self.trc2_ind]

        self.trc1_ind = loc_ind(inc, self.trc1_ind)
        self.trc2_ind = loc_ind(inc, self.trc2_ind)

        # Delay between gait cycles with speed factor got from joystick
        sleep_ms(int(5 * (2.0 - drx)))

    def diagonal_right_movement(self, drx, dry, inc):
        # Cycle 1
        # L1
        self.ls.position(self.L1[0], degrees=(gaits.dr_L1C[self.trc1_ind] + self.L1P_offset[0]))
        self.ls.position(self.L1[1], degrees=(gaits.dr_L1F[self.trc1_ind] + self.L1P_offset[1]))
        self.ls.position(self.L1[2], degrees=(gaits.dr_L1T[self.trc1_ind] + self.L1P_offset[2]))

        # Save positions
        self.L1P[0] = gaits.dr_L1C[self.trc1_ind]
        self.L1P[1] = gaits.dr_L1F[self.trc1_ind]
        self.L1P[2] = gaits.dr_L1T[self.trc1_ind]

        # L3
        self.ls.position(self.L3[0], degrees=(gaits.dr_L3C[self.trc1_ind] + self.L3P_offset[0]))
        self.ls.position(self.L3[1], degrees=(gaits.dr_L3F[self.trc1_ind] + self.L3P_offset[1]))
        self.ls.position(self.L3[2], degrees=(gaits.dr_L3T[self.trc1_ind] + self.L3P_offset[2]))

        # Save positions
        self.L3P[0] = gaits.dr_L3C[self.trc1_ind]
        self.L3P[1] = gaits.dr_L3F[self.trc1_ind]
        self.L3P[2] = gaits.dr_L3T[self.trc1_ind]

        # R2
        self.rs.position(self.R2[0], degrees=(gaits.dr_R2C[self.trc1_ind] + self.R2P_offset[0]))
        self.rs.position(self.R2[1], degrees=(gaits.dr_R2F[self.trc1_ind] + self.R2P_offset[1]))
        self.rs.position(self.R2[2], degrees=(gaits.dr_R2T[self.trc1_ind] + self.R2P_offset[2]))

        # Save positions
        self.R2P[0] = gaits.dr_R2C[self.trc1_ind]
        self.R2P[1] = gaits.dr_R2F[self.trc1_ind]
        self.R2P[2] = gaits.dr_R2T[self.trc1_ind]

        # Cycle 2
        # R1
        self.rs.position(self.R1[0], degrees=(gaits.dr_R1C[self.trc2_ind] + self.R1P_offset[0]))
        self.rs.position(self.R1[1], degrees=(gaits.dr_R1F[self.trc2_ind] + self.R1P_offset[1]))
        self.rs.position(self.R1[2], degrees=(gaits.dr_R1T[self.trc2_ind] + self.R1P_offset[2]))

        # Save positions
        self.R1P[0] = gaits.dr_R1C[self.trc2_ind]
        self.R1P[1] = gaits.dr_R1F[self.trc2_ind]
        self.R1P[2] = gaits.dr_R1T[self.trc2_ind]

        # R3
        self.rs.position(self.R3[0], degrees=(gaits.dr_R3C[self.trc2_ind] + self.R3P_offset[0]))
        self.rs.position(self.R3[1], degrees=(gaits.dr_R3F[self.trc2_ind] + self.R3P_offset[1]))
        self.rs.position(self.R3[2], degrees=(gaits.dr_R3T[self.trc2_ind] + self.R3P_offset[2]))

        # Save positions
        self.R3P[0] = gaits.dr_R3C[self.trc2_ind]
        self.R3P[1] = gaits.dr_R3F[self.trc2_ind]
        self.R3P[2] = gaits.dr_R3T[self.trc2_ind]

        # L2
        self.ls.position(self.L2[0], degrees=(gaits.dr_L2C[self.trc2_ind] + self.L2P_offset[0]))
        self.ls.position(self.L2[1], degrees=(gaits.dr_L2F[self.trc2_ind] + self.L2P_offset[1]))
        self.ls.position(self.L2[2], degrees=(gaits.dr_L2T[self.trc2_ind] + self.L2P_offset[2]))

        # Save positions
        self.L2P[0] = gaits.dr_L2C[self.trc2_ind]
        self.L2P[1] = gaits.dr_L2F[self.trc2_ind]
        self.L2P[2] = gaits.dr_L2T[self.trc2_ind]

        self.trc1_ind = loc_ind(inc, self.trc1_ind)
        self.trc2_ind = loc_ind(inc, self.trc2_ind)

        # Delay between gait cycles with speed factor got from joystick
        sleep_ms(int(5 * (2.0 - max(dry, drx))))

    def diagonal_left_movement(self, drx, dry, inc):
        # Cycle 1
        # L1
        self.ls.position(self.L1[0], degrees=(gaits.dl_L1C[self.trc1_ind] + self.L1P_offset[0]))
        self.ls.position(self.L1[1], degrees=(gaits.dl_L1F[self.trc1_ind] + self.L1P_offset[1]))
        self.ls.position(self.L1[2], degrees=(gaits.dl_L1T[self.trc1_ind] + self.L1P_offset[2]))

        # Save positions
        self.L1P[0] = gaits.dl_L1C[self.trc1_ind]
        self.L1P[1] = gaits.dl_L1F[self.trc1_ind]
        self.L1P[2] = gaits.dl_L1T[self.trc1_ind]

        # L3
        self.ls.position(self.L3[0], degrees=(gaits.dl_L3C[self.trc1_ind] + self.L3P_offset[0]))
        self.ls.position(self.L3[1], degrees=(gaits.dl_L3F[self.trc1_ind] + self.L3P_offset[1]))
        self.ls.position(self.L3[2], degrees=(gaits.dl_L3T[self.trc1_ind] + self.L3P_offset[2]))

        # Save positions
        self.L3P[0] = gaits.dl_L3C[self.trc1_ind]
        self.L3P[1] = gaits.dl_L3F[self.trc1_ind]
        self.L3P[2] = gaits.dl_L3T[self.trc1_ind]

        # R2
        self.rs.position(self.R2[0], degrees=(gaits.dl_R2C[self.trc1_ind] + self.R2P_offset[0]))
        self.rs.position(self.R2[1], degrees=(gaits.dl_R2F[self.trc1_ind] + self.R2P_offset[1]))
        self.rs.position(self.R2[2], degrees=(gaits.dl_R2T[self.trc1_ind] + self.R2P_offset[2]))

        # Save positions
        self.R2P[0] = gaits.dl_R2C[self.trc1_ind]
        self.R2P[1] = gaits.dl_R2F[self.trc1_ind]
        self.R2P[2] = gaits.dl_R2T[self.trc1_ind]

        # Cycle 2
        # R1
        self.rs.position(self.R1[0], degrees=(gaits.dl_R1C[self.trc2_ind] + self.R1P_offset[0]))
        self.rs.position(self.R1[1], degrees=(gaits.dl_R1F[self.trc2_ind] + self.R1P_offset[1]))
        self.rs.position(self.R1[2], degrees=(gaits.dl_R1T[self.trc2_ind] + self.R1P_offset[2]))

        # Save positions
        self.R1P[0] = gaits.dl_R1C[self.trc2_ind]
        self.R1P[1] = gaits.dl_R1F[self.trc2_ind]
        self.R1P[2] = gaits.dl_R1T[self.trc2_ind]

        # R3
        self.rs.position(self.R3[0], degrees=(gaits.dl_R3C[self.trc2_ind] + self.R3P_offset[0]))
        self.rs.position(self.R3[1], degrees=(gaits.dl_R3F[self.trc2_ind] + self.R3P_offset[1]))
        self.rs.position(self.R3[2], degrees=(gaits.dl_R3T[self.trc2_ind] + self.R3P_offset[2]))

        # Save positions
        self.R3P[0] = gaits.dl_R3C[self.trc2_ind]
        self.R3P[1] = gaits.dl_R3F[self.trc2_ind]
        self.R3P[2] = gaits.dl_R3T[self.trc2_ind]

        # L2
        self.ls.position(self.L2[0], degrees=(gaits.dl_L2C[self.trc2_ind] + self.L2P_offset[0]))
        self.ls.position(self.L2[1], degrees=(gaits.dl_L2F[self.trc2_ind] + self.L2P_offset[1]))
        self.ls.position(self.L2[2], degrees=(gaits.dl_L2T[self.trc2_ind] + self.L2P_offset[2]))

        # Save positions
        self.L2P[0] = gaits.dl_L2C[self.trc2_ind]
        self.L2P[1] = gaits.dl_L2F[self.trc2_ind]
        self.L2P[2] = gaits.dl_L2T[self.trc2_ind]

        self.trc1_ind = loc_ind(inc, self.trc1_ind)
        self.trc2_ind = loc_ind(inc, self.trc2_ind)

        # Delay between gait cycles with speed factor got from joystick
        sleep_ms(int(5 * (2.0 - max(dry, drx))))

    def rotate_movement(self, drx, dry, inc):
        # Cycle 1
        # L1
        self.ls.position(self.L1[0], degrees=(gaits.rm_L1C[self.trc1_ind] + self.L1P_offset[0]))
        self.ls.position(self.L1[1], degrees=(gaits.rm_L1F[self.trc1_ind] + self.L1P_offset[1]))
        self.ls.position(self.L1[2], degrees=(gaits.rm_L1T[self.trc1_ind] + self.L1P_offset[2]))

        # Save positions
        self.L1P[0] = gaits.rm_L1C[self.trc1_ind]
        self.L1P[1] = gaits.rm_L1F[self.trc1_ind]
        self.L1P[2] = gaits.rm_L1T[self.trc1_ind]

        # L3
        self.ls.position(self.L3[0], degrees=(gaits.rm_L3C[self.trc1_ind] + self.L3P_offset[0]))
        self.ls.position(self.L3[1], degrees=(gaits.rm_L3F[self.trc1_ind] + self.L3P_offset[1]))
        self.ls.position(self.L3[2], degrees=(gaits.rm_L3T[self.trc1_ind] + self.L3P_offset[2]))

        # Save positions
        self.L3P[0] = gaits.rm_L3C[self.trc1_ind]
        self.L3P[1] = gaits.rm_L3F[self.trc1_ind]
        self.L3P[2] = gaits.rm_L3T[self.trc1_ind]

        # R2
        self.rs.position(self.R2[0], degrees=(gaits.rm_R2C[self.trc1_ind] + self.R2P_offset[0]))
        self.rs.position(self.R2[1], degrees=(gaits.rm_R2F[self.trc1_ind] + self.R2P_offset[1]))
        self.rs.position(self.R2[2], degrees=(gaits.rm_R2T[self.trc1_ind] + self.R2P_offset[2]))

        # Save positions
        self.R2P[0] = gaits.rm_R2C[self.trc1_ind]
        self.R2P[1] = gaits.rm_R2F[self.trc1_ind]
        self.R2P[2] = gaits.rm_R2T[self.trc1_ind]

        # Cycle 2
        # R1
        self.rs.position(self.R1[0], degrees=(gaits.rm_R1C[self.trc2_ind] + self.R1P_offset[0]))
        self.rs.position(self.R1[1], degrees=(gaits.rm_R1F[self.trc2_ind] + self.R1P_offset[1]))
        self.rs.position(self.R1[2], degrees=(gaits.rm_R1T[self.trc2_ind] + self.R1P_offset[2]))

        # Save positions
        self.R1P[0] = gaits.rm_R1C[self.trc2_ind]
        self.R1P[1] = gaits.rm_R1F[self.trc2_ind]
        self.R1P[2] = gaits.rm_R1T[self.trc2_ind]

        # R3
        self.rs.position(self.R3[0], degrees=(gaits.rm_R3C[self.trc2_ind] + self.R3P_offset[0]))
        self.rs.position(self.R3[1], degrees=(gaits.rm_R3F[self.trc2_ind] + self.R3P_offset[1]))
        self.rs.position(self.R3[2], degrees=(gaits.rm_R3T[self.trc2_ind] + self.R3P_offset[2]))

        # Save positions
        self.R3P[0] = gaits.rm_R3C[self.trc2_ind]
        self.R3P[1] = gaits.rm_R3F[self.trc2_ind]
        self.R3P[2] = gaits.rm_R3T[self.trc2_ind]

        # L2
        self.ls.position(self.L2[0], degrees=(gaits.rm_L2C[self.trc2_ind] + self.L2P_offset[0]))
        self.ls.position(self.L2[1], degrees=(gaits.rm_L2F[self.trc2_ind] + self.L2P_offset[1]))
        self.ls.position(self.L2[2], degrees=(gaits.rm_L2T[self.trc2_ind] + self.L2P_offset[2]))

        # Save positions
        self.L2P[0] = gaits.rm_L2C[self.trc2_ind]
        self.L2P[1] = gaits.rm_L2F[self.trc2_ind]
        self.L2P[2] = gaits.rm_L2T[self.trc2_ind]

        self.trc1_ind = loc_ind(inc, self.trc1_ind)
        self.trc2_ind = loc_ind(inc, self.trc2_ind)

        # Delay between gait cycles with speed factor got from joystick
        sleep_ms(int(5 * (2.0 - max(drx, dry))))

    def body_elevation(self, rise):
        # Only the Femur and Tarsus is moved
        # Move FEMUR on left side
        self.ls.position(self.L1[1], degrees=(gaits.em_L1F[self.rt_ind] + self.L1P_offset[1]))
        self.ls.position(self.L2[1], degrees=(gaits.em_L2F[self.rt_ind] + self.L2P_offset[1]))
        self.ls.position(self.L3[1], degrees=(gaits.em_L3F[self.rt_ind] + self.L3P_offset[1]))

        # Move FEMUR on right side
        self.rs.position(self.R1[1], degrees=(gaits.em_R1F[self.rt_ind] + self.R1P_offset[1]))
        self.rs.position(self.R2[1], degrees=(gaits.em_R2F[self.rt_ind] + self.R2P_offset[1]))
        self.rs.position(self.R3[1], degrees=(gaits.em_R3F[self.rt_ind] + self.R3P_offset[1]))

        # Move Tarsus on left side
        self.ls.position(self.L1[2], degrees=(gaits.em_L1T[self.rt_ind] + self.L1P_offset[2]))
        self.ls.position(self.L2[2], degrees=(gaits.em_L2T[self.rt_ind] + self.L2P_offset[2]))
        self.ls.position(self.L3[2], degrees=(gaits.em_L3T[self.rt_ind] + self.L3P_offset[2]))

        # Move Tarsus on right side
        self.rs.position(self.R1[2], degrees=(gaits.em_R1T[self.rt_ind] + self.R1P_offset[2]))
        self.rs.position(self.R2[2], degrees=(gaits.em_R2T[self.rt_ind] + self.R2P_offset[2]))
        self.rs.position(self.R3[2], degrees=(gaits.em_R3T[self.rt_ind] + self.R3P_offset[2]))

        rot_ind(rise, self.rt_ind)

        sleep_ms(5)

    def yaw_rotation(self, lx=0, ly=0):
        # TODO: Write Hexapod rotation around yaw axis
        pass

    def pitch_rotation(self, rx=0, ry=0):
        # TODO: Write Hexapod rotation around pitch axis
        pass

    def roll_rotation(self, right):
        # TODO: Write Hexapod rotation around roll axis
        pass

    def sit_down(self):
        # TODO: Write a sit down gait for the Hexapod
        # TODO: Wait for the gait to complete
        # TODO: Send a "DONE" message to the app
        pass

    def get_up(self):
        # TODO: Write a get up gait for the Hexapod
        # TODO: Wait for the gait to complete
        # TODO: Send a "DONE" message to the app
        pass

    """
    LOCOMOTION TEST CASES FOR DEBUGGING
    DELETE AFTER USE
    """

    def tripod_test(self, t, leg):
        if leg == "R1":
            for i in range(50):
                self.rs.position(self.R1[0], degrees=(gaits.vm_R1C[i] + self.R1P_offset[0]))
                self.rs.position(self.R1[1], degrees=(gaits.vm_R1F[i] + self.R1P_offset[1]))
                self.rs.position(self.R1[2], degrees=(gaits.vm_R1T[i] + self.R1P_offset[2]))
                sleep_ms(t)
        elif leg == "R2":
            for i in range(50):
                self.rs.position(self.R2[0], degrees=(gaits.vm_R2C[i] + self.R2P_offset[0]))
                self.rs.position(self.R2[1], degrees=(gaits.vm_R2F[i] + self.R2P_offset[1]))
                self.rs.position(self.R2[2], degrees=(gaits.vm_R2T[i] + self.R2P_offset[2]))
                sleep_ms(t)
        elif leg == "R3":
            for i in range(50):
                self.rs.position(self.R3[0], degrees=(gaits.vm_R3C[i] + self.R3P_offset[0]))
                self.rs.position(self.R3[1], degrees=(gaits.vm_R3F[i] + self.R3P_offset[1]))
                self.rs.position(self.R3[2], degrees=(gaits.vm_R3T[i] + self.R3P_offset[2]))
                sleep_ms(t)
        elif leg == "L1":
            for i in range(50):
                self.ls.position(self.L1[0], degrees=(gaits.vm_L1C[i] + self.L1P_offset[0]))
                self.ls.position(self.L1[1], degrees=(gaits.vm_L1F[i] + self.L1P_offset[1]))
                self.ls.position(self.L1[2], degrees=(gaits.vm_L1T[i] + self.L1P_offset[2]))
                sleep_ms(t)
        elif leg == "L2":
            for i in range(50):
                self.ls.position(self.L2[0], degrees=(gaits.vm_L2C[i] + self.L2P_offset[0]))
                self.ls.position(self.L2[1], degrees=(gaits.vm_L2F[i] + self.L2P_offset[1]))
                self.ls.position(self.L2[2], degrees=(gaits.vm_L2T[i] + self.L2P_offset[2]))
                sleep_ms(t)
        elif leg == "L3":
            for i in range(50):
                self.ls.position(self.L3[0], degrees=(gaits.vm_L3C[i] + self.L3P_offset[0]))
                self.ls.position(self.L3[1], degrees=(gaits.vm_L3F[i] + self.L3P_offset[1]))
                self.ls.position(self.L3[2], degrees=(gaits.vm_L3T[i] + self.L3P_offset[2]))
                sleep_ms(t)

    def tripod_test_cycles(self, t, cycles):
        c1 = 0
        c2 = ceil(len(gaits.vm_R1C) / 2)

        for _ in range(cycles):
            for i in range(len(gaits.vm_R1C)):
                # Cycle 1
                self.ls.position(self.L1[0], degrees=(gaits.vm_L1C[c1] + self.L1P_offset[0]))
                self.ls.position(self.L1[1], degrees=(gaits.vm_L1F[c1] + self.L1P_offset[1]))
                self.ls.position(self.L1[2], degrees=(gaits.vm_L1T[c1] + self.L1P_offset[2]))

                self.rs.position(self.R2[0], degrees=(gaits.vm_R2C[c1] + self.R2P_offset[0]))
                self.rs.position(self.R2[1], degrees=(gaits.vm_R2F[c1] + self.R2P_offset[1]))
                self.rs.position(self.R2[2], degrees=(gaits.vm_R2T[c1] + self.R2P_offset[2]))

                self.ls.position(self.L3[0], degrees=(gaits.vm_L3C[c1] + self.L3P_offset[0]))
                self.ls.position(self.L3[1], degrees=(gaits.vm_L3F[c1] + self.L3P_offset[1]))
                self.ls.position(self.L3[2], degrees=(gaits.vm_L3T[c1] + self.L3P_offset[2]))

                # Cycle 2
                self.rs.position(self.R3[0], degrees=(gaits.vm_R3C[c2] + self.R3P_offset[0]))
                self.rs.position(self.R3[1], degrees=(gaits.vm_R3F[c2] + self.R3P_offset[1]))
                self.rs.position(self.R3[2], degrees=(gaits.vm_R3T[c2] + self.R3P_offset[2]))

                self.ls.position(self.L2[0], degrees=(gaits.vm_L2C[c2] + self.L2P_offset[0]))
                self.ls.position(self.L2[1], degrees=(gaits.vm_L2F[c2] + self.L2P_offset[1]))
                self.ls.position(self.L2[2], degrees=(gaits.vm_L2T[c2] + self.L2P_offset[2]))

                self.rs.position(self.R1[0], degrees=(gaits.vm_R1C[c2] + self.R1P_offset[0]))
                self.rs.position(self.R1[1], degrees=(gaits.vm_R1F[c2] + self.R1P_offset[1]))
                self.rs.position(self.R1[2], degrees=(gaits.vm_R1T[c2] + self.R1P_offset[2]))

                c1 = loc_ind(True, c1)
                c2 = loc_ind(True, c2)

                sleep_ms(t)

    def body_elevation_test(self, rise):
        # If rise is True, the body elevation will rise
        # If rise is False, the body elevation will lower
        gaits.em(rise)

        # Only the Femur and Tarsus is moved
        # Move FEMUR on left side
        self.ls.position(self.L1[1], degrees=(gaits.vm_L1F[gaits.vm.i] + self.L1P_offset[1]))
        self.ls.position(self.L2[1], degrees=(gaits.vm_L2F[gaits.vm.i] + self.L2P_offset[1]))
        self.ls.position(self.L3[1], degrees=(gaits.vm_L3F[gaits.vm.i] + self.L3P_offset[1]))

        # Move FEMUR on right side
        self.rs.position(self.R1[1], degrees=(gaits.vm_R1F[gaits.vm.i] + self.R1P_offset[1]))
        self.rs.position(self.R2[1], degrees=(gaits.vm_R2F[gaits.vm.i] + self.R2P_offset[1]))
        self.rs.position(self.R3[1], degrees=(gaits.vm_R3F[gaits.vm.i] + self.R3P_offset[1]))

        # Move Tarsus on left side
        self.ls.position(self.L1[2], degrees=(gaits.vm_L1T[gaits.vm.i] + self.L1P_offset[2]))
        self.ls.position(self.L2[2], degrees=(gaits.vm_L2T[gaits.vm.i] + self.L2P_offset[2]))
        self.ls.position(self.L3[2], degrees=(gaits.vm_L3T[gaits.vm.i] + self.L3P_offset[2]))

        # Move Tarsus on right side
        self.rs.position(self.R1[2], degrees=(gaits.vm_R1T[gaits.vm.i] + self.R1P_offset[2]))
        self.rs.position(self.R2[2], degrees=(gaits.vm_R2T[gaits.vm.i] + self.R2P_offset[2]))
        self.rs.position(self.R3[2], degrees=(gaits.vm_R3T[gaits.vm.i] + self.R3P_offset[2]))

        sleep_ms(5)
