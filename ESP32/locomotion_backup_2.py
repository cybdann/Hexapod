from servo import Servos
from machine import I2C
from utime import sleep_ms

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


class Locomotion:
    def __init__(self, i2c=None, gait=b'TR', mode=b'A', walk=False, esp=False, stopped=False):
        # Set default I2C peripherals if none is provided
        if i2c is None:
            i2c = I2C(0)
        else:
            self.i2c = i2c

        # PWM boards list
        self.left_side = Servos(i2c, address=0x41)
        self.right_side = Servos(i2c, address=0x40)

        # Set max and min duty for servos drivers
        # FOR THE LOVE OF GOD, LEAVE THIS AS IT IS, UNLESS YOU WANT BURNT DOWN SERVOS
        self.right_side.max_duty = 580
        self.left_side.max_duty = 580

        self.right_side.min_duty = 160
        self.left_side.min_duty = 160

        # Servo index list for each leg
        # First index is COXA, second is FEMUR and the last one is TARSUS
        self.L1 = [9, 10, 11]
        self.L2 = [5, 6, 7]
        self.L3 = [2, 1, 0]

        self.R1 = [6, 5, 4]
        self.R2 = [10, 9, 8]
        self.R3 = [13, 14, 15]

        # Servo position list for each leg (Hexapod is powered on while sitting)
        self.L1P = [90, 90, 90]
        self.L2P = [90, 90, 90]
        self.L3P = [90, 90, 90]

        self.R1P = [90, 90, 90]
        self.R2P = [90, 90, 90]
        self.R3P = [90, 90, 90]

        # Servo physical offset in degrees
        self.L1P_offset = [0, 10, -10]
        self.L2P_offset = [5, 10, -10]
        self.L3P_offset = [5, 10, -10]

        self.R1P_offset = [10, -20, -10]
        self.R2P_offset = [0, 25, -10]
        self.R3P_offset = [-10, -30, 0]

        # Hexapod statuses
        self.gait = gait  # Gait selection (TR = Tripod (default), MT = Metachronal)
        self.mode = mode  # Control mode selection (A = A mode (default), B = B mode)

        self.walk = walk  # Is the robot standing?
        self.esp = esp  # Electronic stability control
        self.stopped = stopped  # All servos stopped

        # Tripod cycle
        self.tripod_cycle = True

        # Vertical movement
        self.iv = 0
        # Right side vertical movement
        self.vert_R1C = [89, 86, 82, 77, 73, 68, 62, 57, 51, 44, 38, 32, 27, 30, 33, 36, 39, 43, 46, 50, 53, 56, 60, 63,
                         67, 70, 74, 77, 81, 84, 88, 91, 95, 98, 102, 105, 109, 112, 111, 110, 109, 108, 106, 105, 103,
                         101, 99, 97, 95, 92]
        self.vert_R1F = [91, 91, 91, 90, 90, 90, 89, 89, 89, 89, 89, 89, 89, 103, 116, 128, 139, 148, 155, 158, 159,
                         159, 157, 155, 152, 148, 144, 140, 136, 131, 125, 120, 114, 107, 101, 93, 86, 79, 81, 83, 84,
                         86, 87, 88, 89, 90, 91, 91, 91, 91]
        self.vert_R1T = [93, 94, 95, 96, 97, 98, 98, 99, 99, 99, 99, 98, 98, 105, 112, 117, 121, 124, 124, 123, 121,
                         118, 114, 110, 107, 103, 99, 96, 92, 89, 86, 82, 79, 75, 70, 66, 61, 56, 60, 64, 68, 71, 74,
                         77, 80, 83, 85, 87, 89, 91]

        self.vert_R2C = [88, 84, 80, 76, 72, 68, 64, 61, 58, 55, 52, 49, 47, 50, 54, 57, 61, 64, 68, 71, 75, 78, 82, 85,
                         89, 92, 96, 99, 103, 106, 110, 113, 117, 120, 124, 127, 131, 134, 132, 129, 126, 123, 120, 117,
                         113, 109, 105, 101, 97, 93]
        self.vert_R2F = [91, 91, 91, 91, 91, 91, 91, 91, 91, 90, 90, 89, 89, 97, 105, 112, 118, 124, 128, 132, 135, 137,
                         138, 139, 140, 140, 139, 138, 137, 135, 132, 128, 124, 118, 112, 105, 97, 89, 89, 90, 90, 91,
                         91, 91, 91, 91, 91, 91, 91, 91]
        self.vert_R2T = [92, 92, 91, 91, 90, 89, 88, 87, 86, 84, 82, 80, 78, 82, 86, 89, 91, 92, 93, 94, 94, 94, 94, 93,
                         93, 93, 93, 94, 94, 94, 94, 93, 92, 91, 89, 86, 82, 78, 80, 82, 84, 86, 87, 88, 89, 90, 91, 91,
                         92, 92]

        self.vert_R3C = [89, 86, 84, 82, 80, 78, 76, 75, 73, 72, 71, 70, 69, 72, 76, 79, 83, 86, 90, 93, 97, 100, 104,
                         107, 111, 114, 118, 121, 125, 128, 131, 135, 138, 142, 145, 148, 151, 154, 149, 143, 137, 130,
                         124, 119, 113, 108, 104, 99, 95, 92]
        self.vert_R3F = [91, 91, 91, 91, 90, 89, 88, 87, 86, 84, 83, 81, 79, 86, 93, 101, 107, 114, 120, 125, 131, 136,
                         140, 144, 148, 152, 155, 157, 159, 159, 158, 155, 148, 139, 128, 116, 103, 89, 89, 89, 89, 89,
                         89, 89, 90, 90, 90, 91, 91, 91]
        self.vert_R3T = [91, 89, 87, 85, 83, 80, 77, 74, 71, 68, 64, 60, 56, 61, 66, 70, 75, 79, 82, 86, 89, 92, 96, 99,
                         103, 107, 110, 114, 118, 121, 123, 124, 124, 121, 117, 112, 105, 98, 98, 99, 99, 99, 99, 98,
                         98, 97, 96, 95, 94, 93]

        self.vert_L1C = [92, 95, 99, 104, 108, 113, 119, 124, 130, 137, 143, 149, 154, 151, 148, 145, 142, 138, 135,
                         131, 128, 125, 121, 118, 114, 111, 107, 104, 100, 97, 93, 90, 86, 83, 79, 76, 72, 69, 70, 71,
                         72, 73, 75, 76, 78, 80, 82, 84, 86, 89]
        self.vert_L1F = [89, 89, 89, 90, 90, 90, 91, 91, 91, 91, 91, 91, 91, 77, 64, 52, 41, 32, 25, 22, 21, 21, 23, 25,
                         28, 32, 36, 40, 44, 49, 55, 60, 66, 73, 79, 87, 94, 101, 99, 97, 96, 94, 93, 92, 91, 90, 89,
                         89, 89, 89]
        self.vert_L1T = [87, 86, 85, 84, 83, 82, 82, 81, 81, 81, 81, 82, 82, 75, 68, 63, 59, 56, 56, 57, 59, 62, 66, 70,
                         73, 77, 81, 84, 88, 91, 94, 98, 101, 105, 110, 114, 119, 124, 120, 116, 112, 109, 106, 103,
                         100, 97, 95, 93, 91, 89]

        self.vert_L2C = [93, 97, 101, 105, 109, 113, 117, 120, 123, 126, 129, 132, 134, 131, 127, 124, 120, 117, 113,
                         110, 106, 103, 99, 96, 92, 89, 85, 82, 78, 75, 71, 68, 64, 61, 57, 54, 50, 47, 49, 52, 55, 58,
                         61, 64, 68, 72, 76, 80, 84, 88]
        self.vert_L2F = [89, 89, 89, 89, 89, 89, 89, 89, 89, 90, 90, 91, 91, 83, 75, 68, 62, 56, 52, 48, 45, 43, 42, 41,
                         40, 40, 41, 42, 43, 45, 48, 52, 56, 62, 68, 75, 83, 91, 91, 90, 90, 89, 89, 89, 89, 89, 89, 89,
                         89, 89]
        self.vert_L2T = [88, 88, 89, 89, 90, 91, 92, 93, 94, 96, 98, 100, 102, 98, 94, 91, 89, 88, 87, 86, 86, 86, 86,
                         87, 87, 87, 87, 86, 86, 86, 86, 87, 88, 89, 91, 94, 98, 102, 100, 98, 96, 94, 93, 92, 91, 90,
                         89, 89, 88, 88]

        self.vert_L3C = [92, 95, 97, 99, 101, 103, 105, 106, 108, 109, 110, 111, 112, 109, 105, 102, 98, 95, 91, 88, 84,
                         81, 77, 74, 70, 67, 63, 60, 56, 53, 50, 46, 43, 39, 36, 33, 30, 27, 32, 38, 44, 51, 57, 62, 68,
                         73, 77, 82, 86, 89]
        self.vert_L3F = [89, 89, 89, 89, 90, 91, 92, 93, 94, 96, 97, 99, 101, 94, 87, 79, 73, 66, 60, 55, 49, 44, 40,
                         36, 32, 28, 25, 23, 21, 21, 22, 25, 32, 41, 52, 64, 77, 91, 91, 91, 91, 91, 91, 91, 90, 90, 90,
                         89, 89, 89]
        self.vert_L3T = [89, 91, 93, 95, 97, 100, 103, 106, 109, 112, 116, 120, 124, 119, 114, 110, 105, 101, 98, 94,
                         91, 88, 84, 81, 77, 73, 70, 66, 62, 59, 57, 56, 56, 59, 63, 68, 75, 82, 82, 81, 81, 81, 81, 82,
                         82, 83, 84, 85, 86, 87]

    def tripod_test(self, t, l):
        if l == "R1":
            for i in range(50):
                self.right_side.position(self.R1[0], degrees=(self.vert_R1C[i] + self.R1P_offset[0]))
                self.right_side.position(self.R1[1], degrees=(self.vert_R1F[i] + self.R1P_offset[1]))
                self.right_side.position(self.R1[2], degrees=(self.vert_R1T[i] + self.R1P_offset[2]))
                sleep_ms(t)
        elif l == "R2":
            for i in range(50):
                self.right_side.position(self.R2[0], degrees=(self.vert_R2C[i] + self.R2P_offset[0]))
                self.right_side.position(self.R2[1], degrees=(self.vert_R2F[i] + self.R2P_offset[1]))
                self.right_side.position(self.R2[2], degrees=(self.vert_R2T[i] + self.R2P_offset[2]))
                sleep_ms(t)
        elif l == "R3":
            for i in range(50):
                self.right_side.position(self.R3[0], degrees=(self.vert_R3C[i] + self.R3P_offset[0]))
                self.right_side.position(self.R3[1], degrees=(self.vert_R3F[i] + self.R3P_offset[1]))
                self.right_side.position(self.R3[2], degrees=(self.vert_R3T[i] + self.R3P_offset[2]))
                sleep_ms(t)
        elif l == "L1":
            for i in range(50):
                self.left_side.position(self.L1[0], degrees=(self.vert_L1C[i] + self.L1P_offset[0]))
                self.left_side.position(self.L1[1], degrees=(self.vert_L1F[i] + self.L1P_offset[1]))
                self.left_side.position(self.L1[2], degrees=(self.vert_L1T[i] + self.L1P_offset[2]))
                sleep_ms(t)
        elif l == "L2":
            for i in range(50):
                self.left_side.position(self.L2[0], degrees=(self.vert_L2C[i] + self.L2P_offset[0]))
                self.left_side.position(self.L2[1], degrees=(self.vert_L2F[i] + self.L2P_offset[1]))
                self.left_side.position(self.L2[2], degrees=(self.vert_L2T[i] + self.L2P_offset[2]))
                sleep_ms(t)
        elif l == "L3":
            for i in range(50):
                self.left_side.position(self.L3[0], degrees=(self.vert_L3C[i] + self.L3P_offset[0]))
                self.left_side.position(self.L3[1], degrees=(self.vert_L3F[i] + self.L3P_offset[1]))
                self.left_side.position(self.L3[2], degrees=(self.vert_L3T[i] + self.L3P_offset[2]))
                sleep_ms(t)

    def tripod_test_cycles(self, t, cycles):
        for _ in range(cycles):
            for i in range(50):
                self.left_side.position(self.L1[0], degrees=(self.vert_L1C[i] + self.L1P_offset[0]))
                self.left_side.position(self.L1[1], degrees=(self.vert_L1F[i] + self.L1P_offset[1]))
                self.left_side.position(self.L1[2], degrees=(self.vert_L1T[i] + self.L1P_offset[2]))

                self.right_side.position(self.R2[0], degrees=(self.vert_R2C[i] + self.R2P_offset[0]))
                self.right_side.position(self.R2[1], degrees=(self.vert_R2F[i] + self.R2P_offset[1]))
                self.right_side.position(self.R2[2], degrees=(self.vert_R2T[i] + self.R2P_offset[2]))

                self.left_side.position(self.L3[0], degrees=(self.vert_L3C[i] + self.L3P_offset[0]))
                self.left_side.position(self.L3[1], degrees=(self.vert_L3F[i] + self.L3P_offset[1]))
                self.left_side.position(self.L3[2], degrees=(self.vert_L3T[i] + self.L3P_offset[2]))

                sleep_ms(t)

            for i in range(50):
                self.right_side.position(self.R3[0], degrees=(self.vert_R3C[i] + self.R3P_offset[0]))
                self.right_side.position(self.R3[1], degrees=(self.vert_R3F[i] + self.R3P_offset[1]))
                self.right_side.position(self.R3[2], degrees=(self.vert_R3T[i] + self.R3P_offset[2]))

                self.left_side.position(self.L2[0], degrees=(self.vert_L2C[i] + self.L2P_offset[0]))
                self.left_side.position(self.L2[1], degrees=(self.vert_L2F[i] + self.L2P_offset[1]))
                self.left_side.position(self.L2[2], degrees=(self.vert_L2T[i] + self.L2P_offset[2]))

                self.right_side.position(self.R1[0], degrees=(self.vert_R1C[i] + self.R1P_offset[0]))
                self.right_side.position(self.R1[1], degrees=(self.vert_R1F[i] + self.R1P_offset[1]))
                self.right_side.position(self.R1[2], degrees=(self.vert_R1T[i] + self.R1P_offset[2]))

                sleep_ms(t)

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
            self.left_side.position(self.L1[servo], degrees=(self.L1P[servo] + self.L1P_offset[servo]))
            self.left_side.position(self.L2[servo], degrees=(self.L2P[servo] + self.L2P_offset[servo]))
            self.left_side.position(self.L3[servo], degrees=(self.L3P[servo] + self.L3P_offset[servo]))

            # Move right  side servos
            self.right_side.position(self.R1[servo], degrees=(self.R1P[servo] + self.R1P_offset[servo]))
            self.right_side.position(self.R2[servo], degrees=(self.R2P[servo] + self.R2P_offset[servo]))
            self.right_side.position(self.R3[servo], degrees=(self.R3P[servo] + self.R3P_offset[servo]))

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

            self.L1P[0] = self.L1P[1] if self.L1P[0] == 90 else \
                ((self.L1P[0] - 1) if self.L1P[0] > 90 else (self.L1P[0] + 1))
            self.L2P[0] = self.L2P[1] if self.L2P[0] == 90 else \
                ((self.L2P[0] - 1) if self.L2P[0] > 90 else (self.L2P[0] + 1))
            self.L3P[0] = self.L3P[1] if self.L3P[0] == 90 else \
                ((self.L3P[0] - 1) if self.L3P[0] > 90 else (self.L3P[0] + 1))

            # Move COXA
            self.right_side.position(self.R1[0], degrees=(self.R1P[0] + self.R1P_offset[0]))
            self.right_side.position(self.R2[0], degrees=(self.R2P[0] + self.R2P_offset[0]))
            self.right_side.position(self.R3[0], degrees=(self.R3P[0] + self.R3P_offset[0]))

            self.left_side.position(self.L1[0], degrees=(self.L1P[0] + self.L1P_offset[0]))
            self.left_side.position(self.L2[0], degrees=(self.L2P[0] + self.L2P_offset[0]))
            self.left_side.position(self.L3[0], degrees=(self.L3P[0] + self.L3P_offset[0]))

            # Delay for next increment
            sleep_ms(5)

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
            self.right_side.position(self.R1[1], degrees=(self.R1P[1] + self.R1P_offset[1]))
            self.right_side.position(self.R2[1], degrees=(self.R2P[1] + self.R2P_offset[1]))
            self.right_side.position(self.R3[1], degrees=(self.R3P[1] + self.R3P_offset[1]))

            self.left_side.position(self.L1[1], degrees=(self.L1P[1] + self.L1P_offset[1]))
            self.left_side.position(self.L2[1], degrees=(self.L2P[1] + self.L2P_offset[1]))
            self.left_side.position(self.L3[1], degrees=(self.L3P[1] + self.L3P_offset[1]))

            # Delay for next increment
            sleep_ms(5)

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
            self.right_side.position(self.R1[2], degrees=(self.R1P[2] + self.R1P_offset[2]))
            self.right_side.position(self.R2[2], degrees=(self.R2P[2] + self.R2P_offset[2]))
            self.right_side.position(self.R3[2], degrees=(self.R3P[2] + self.R3P_offset[2]))

            self.left_side.position(self.L1[2], degrees=(self.L1P[2] + self.L1P_offset[2]))
            self.left_side.position(self.L2[2], degrees=(self.L2P[2] + self.L2P_offset[2]))
            self.left_side.position(self.L3[2], degrees=(self.L3P[2] + self.L3P_offset[2]))

            # Delay for next increment
            sleep_ms(5)

            # Check if every servo is at 90 degrees
            if self.R1P[2] == 90 and self.R2P[2] == 90 and self.R3P[2] == 90 and \
                    self.L1P[2] == 90 and self.L2P[2] == 90 and self.L3P[2] == 90:
                flag = False

    def tripod(self, rx=0, ry=0):
        # TODO: ALL THIS SHIT IS FOR THE RIGHT SIDE OF THE HEXAPOD
        # TODO: WRITE CODE FOR THE LEFT SIDE OF THE ROBOT
        # Delay percentage got from joystick
        try:
            dRY = float(ry)
            dRX = float(rx)
        except ValueError:
            return

        # Joystick isn't moved or done walk
        if dRY == 0.0 and dRX == 0.0:
            # Set Hexapod into normal position
            self.set_default_position()
            return

        # Check for walking direction for each axis
        directionRY = True if dRY >= 0.0 else False  # True is forward, False is backwards
        directionRX = True if dRX >= 0.0 else False  # True is right, False is left

        # Vertical movement forward (Reference servo - R2C - Right Side Middle COXA)
        if directionRY:
            # Forward cycle
            self.iv += 1
        else:
            # Backwards cycle
            self.iv -= 1

        # Index for running through the vertical movement list
        if self.iv == 50:
            self.tripod_cycle = not self.tripod_cycle
            self.iv = 0
        elif self.iv == -1:
            self.tripod_cycle = not self.tripod_cycle
            self.iv = 49

        if self.tripod_cycle:
            # L1
            self.left_side.position(self.L1[0], degrees=(self.vert_L1C[self.iv] + self.L1P_offset[0]))
            self.left_side.position(self.L1[1], degrees=(self.vert_L1F[self.iv] + self.L1P_offset[1]))
            self.left_side.position(self.L1[2], degrees=(self.vert_L1T[self.iv] + self.L1P_offset[2]))

            # Save positions
            self.L1P[0] = self.vert_L1C[self.iv]
            self.L1P[1] = self.vert_L1F[self.iv]
            self.L1P[2] = self.vert_L1T[self.iv]

            # L3
            self.left_side.position(self.L3[0], degrees=(self.vert_L3C[self.iv] + self.L3P_offset[0]))
            self.left_side.position(self.L3[1], degrees=(self.vert_L3F[self.iv] + self.L3P_offset[1]))
            self.left_side.position(self.L3[2], degrees=(self.vert_L3T[self.iv] + self.L3P_offset[2]))

            # Save positions
            self.L3P[0] = self.vert_L3C[self.iv]
            self.L3P[1] = self.vert_L3F[self.iv]
            self.L3P[2] = self.vert_L3T[self.iv]

            # R2
            self.right_side.position(self.R2[0], degrees=(self.vert_R2C[self.iv] + self.R2P_offset[0]))
            self.right_side.position(self.R2[1], degrees=(self.vert_R2F[self.iv] + self.R2P_offset[1]))
            self.right_side.position(self.R2[2], degrees=(self.vert_R2T[self.iv] + self.R2P_offset[2]))

            # Save positions
            self.R2P[0] = self.vert_R2C[self.iv]
            self.R2P[1] = self.vert_R2F[self.iv]
            self.R2P[2] = self.vert_R2T[self.iv]
        else:

            # R1
            self.right_side.position(self.R1[0], degrees=(self.vert_R1C[self.iv] + self.R1P_offset[0]))
            self.right_side.position(self.R1[1], degrees=(self.vert_R1F[self.iv] + self.R1P_offset[1]))
            self.right_side.position(self.R1[2], degrees=(self.vert_R1T[self.iv] + self.R1P_offset[2]))

            # Save positions
            self.R1P[0] = self.vert_R1C[self.iv]
            self.R1P[1] = self.vert_R1F[self.iv]
            self.R1P[2] = self.vert_R1T[self.iv]

            # R3
            self.right_side.position(self.R3[0], degrees=(self.vert_R3C[self.iv] + self.R3P_offset[0]))
            self.right_side.position(self.R3[1], degrees=(self.vert_R3F[self.iv] + self.R3P_offset[1]))
            self.right_side.position(self.R3[2], degrees=(self.vert_R3T[self.iv] + self.R3P_offset[2]))

            # Save positions
            self.R3P[0] = self.vert_R3C[self.iv]
            self.R3P[1] = self.vert_R3F[self.iv]
            self.R3P[2] = self.vert_R3T[self.iv]

            # L2
            self.left_side.position(self.L2[0], degrees=(self.vert_L2C[self.iv] + self.L2P_offset[0]))
            self.left_side.position(self.L2[1], degrees=(self.vert_L2F[self.iv] + self.L2P_offset[1]))
            self.left_side.position(self.L2[2], degrees=(self.vert_L2T[self.iv] + self.L2P_offset[2]))

            # Save positions
            self.L2P[0] = self.vert_L2C[self.iv]
            self.L2P[1] = self.vert_L2F[self.iv]
            self.L2P[2] = self.vert_L2T[self.iv]

        # Delay between gait cycles with speed factor got from joystick
        sleep_ms(int(7.5 * (2.0 - abs(max(dRX, dRY)))))

    def metachronal(self, rx=0, ry=0):
        # TODO: Write Hexapod Metachronal movement
        pass

    def yaw_rotation(self, lx=0, ly=0):
        # TODO: Write Hexapod rotation around yaw axis
        pass

    def pitch_rotation(self, rx=0, ry=0):
        # TODO: Write Hexapod rotation around pitch axis
        pass

    def roll_rotation(self, right):
        # TODO: Write Hexapod rotation around roll axis
        pass

    def body_elevation(self, rise):
        # If True then raise body (Push leg against the ground)
        if rise and self.L1P[1] > 44:
            # Decrement servo position for FEMUR
            self.L1P[1] += 1
            self.L2P[1] += 1
            self.L3P[1] += 1

            self.R1P[1] -= 1
            self.R2P[1] -= 1
            self.R3P[1] -= 1
        # If False then lower body
        elif not rise and self.L1P[1] < 119:
            # Increment servo position for FEMUR
            self.L1P[1] -= 1
            self.L2P[1] -= 1
            self.L3P[1] -= 1

            self.R1P[1] += 1
            self.R2P[1] += 1
            self.R3P[1] += 1
        # If FEMUR is at max or min servo position, do nothing
        else:
            return

        # Move FEMUR on left side
        self.left_side.position(self.L1[1], degrees=(self.L1P[1] + self.L1P_offset[1]))
        self.left_side.position(self.L2[1], degrees=(self.L2P[1] + self.L2P_offset[1]))
        self.left_side.position(self.L3[1], degrees=(self.L3P[1] + self.L3P_offset[1]))

        # Move FEMUR on right side
        self.right_side.position(self.R1[1], degrees=(self.R1P[1] + self.R1P_offset[1]))
        self.right_side.position(self.R2[1], degrees=(self.R2P[1] + self.R2P_offset[1]))
        self.right_side.position(self.R3[1], degrees=(self.R3P[1] + self.R3P_offset[1]))

        # Delay for next iteration
        sleep_ms(10)

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
