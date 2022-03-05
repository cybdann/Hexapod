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
        
        Controls Fermur -> F
        Controls Pattela -> P
        Controls Tarsus -> T
        
        e.g. L2F servo is found on the left side of the body
        and manipulates the Fermur of the middle leg
        
    Python servo list:
        L1 = [<pwm channel for Fermur>, <pwm channel for Pattela>, <pwm channel for Tarsus>]
        .
        .
        .
        R3 = [<pwm channel for Fermur>, <pwm channel for Pattela>, <pwm channel for Tarsus>]
        
"""


class Locomotion:
    def __init__(self, i2c=None, gait=b'TR', mode=b'A', walk=False, esp=False, stopped=False):
        # Set default I2C peripherals if none is provided
        if i2c is None:
            i2c = I2C(0)
        else:
            self.i2c = i2c

        # PWM boards list
        self.left_side = Servos(i2c, address=0x40)
        self.right_side = Servos(i2c, address=0x41)

        # Set max and min duty for servos drivers
        # FOR THE LOVE OF GOD, LEAVE THIS AS IT IS, UNLESS YOU WANT BURNT DOWN SERVOS
        self.right_side.max_duty = 580
        self.left_side.max_duty = 580

        self.right_side.min_duty = 160
        self.left_side.min_duty = 160

        # Servo index list for each leg
        # First index is COXA, second is FEMUR and the last one is TARSUS
        self.L1 = [13, 14, 15]
        self.L2 = [8, 9, 10]
        self.L3 = [4, 5, 6]

        self.R1 = [13, 14, 15]
        self.R2 = [8, 9, 10]
        self.R3 = [4, 5, 6]

        # Servo position list for each leg (Hexapod is powered on while sitting)
        # TODO: Default position should be the sitting position
        self.L1P = [90, 90, 90]
        self.L2P = [90, 90, 90]
        self.L3P = [90, 90, 90]

        self.R1P = [90, 90, 90]
        self.R2P = [90, 90, 90]
        self.R3P = [90, 90, 90]

        # Hexapod statuses
        self.gait = gait  # Gait selection (TR = Tripod (default), MT = Metachronal)
        self.mode = mode  # Control mode selection (A = A mode (default), B = B mode)

        self.walk = walk  # Is the robot standing?
        self.esp = esp  # Electronic stability control
        self.stopped = stopped  # All servos stopped

        # Tripod gait statuses
        self.t_forward_cycle = True
        self.t_rightward_cycle = True

        # Cycle position increment/decrement
        self.cycle_gain_pos = 3

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
            self.left_side.position(self.L1[servo], degrees=self.L1P[servo])
            self.left_side.position(self.L2[servo], degrees=self.L2P[servo])
            self.left_side.position(self.L3[servo], degrees=self.L3P[servo])

            # Move right  side servos
            self.right_side.position(self.R1[servo], degrees=self.R1P[servo])
            self.right_side.position(self.R2[servo], degrees=self.R2P[servo])
            self.right_side.position(self.R3[servo], degrees=self.R3P[servo])

    def return_to_default_position(self):
        flag = True

        # Return every servo to 90 degrees in cycle_gain_pos increments
        while flag:
            # Calculate COXA servo position
            self.R1P[0] = self.R1P[0] if self.R1P[0] == 90 else \
                ((self.R1P[0] - self.cycle_gain_pos) if self.R1P[0] > 90 else (self.R1P[0] + self.cycle_gain_pos))
            self.R2P[0] = self.R2P[0] if self.R2P[0] == 90 else \
                ((self.R2P[0] - self.cycle_gain_pos) if self.R2P[0] > 90 else (self.R2P[0] + self.cycle_gain_pos))
            self.R3P[0] = self.R3P[0] if self.R3P[0] == 90 else \
                ((self.R3P[0] - self.cycle_gain_pos) if self.R3P[0] > 90 else (self.R3P[0] + self.cycle_gain_pos))

            # Move COXA
            self.right_side.position(self.R1[0], degrees=self.R1P[0])
            self.right_side.position(self.R2[0], degrees=self.R2P[0])
            self.right_side.position(self.R3[0], degrees=self.R3P[0])

            # Delay for next increment
            sleep_ms(10)

            # Check if every servo is at 90 degrees
            if self.R1P[0] == 90 and self.R2P[0] == 90 and self.R3P[0] == 90:
                flag = False

        flag = True

        while flag:
            # Calculate FEMUR servo position
            self.R1P[1] = self.R1P[1] if self.R1P[1] == 90 else \
                ((self.R1P[1] - self.cycle_gain_pos) if self.R1P[1] > 90 else (self.R1P[1] + self.cycle_gain_pos))
            self.R2P[1] = self.R2P[1] if self.R2P[1] == 90 else \
                ((self.R2P[1] - self.cycle_gain_pos) if self.R2P[1] > 90 else (self.R2P[1] + self.cycle_gain_pos))
            self.R3P[1] = self.R3P[1] if self.R3P[1] == 90 else \
                ((self.R3P[1] - self.cycle_gain_pos) if self.R3P[1] > 90 else (self.R3P[1] + self.cycle_gain_pos))

            # Move COXA
            self.right_side.position(self.R1[1], degrees=self.R1P[1])
            self.right_side.position(self.R2[1], degrees=self.R2P[1])
            self.right_side.position(self.R3[1], degrees=self.R3P[1])

            # Delay for next increment
            sleep_ms(10)

            # Check if every servo is at 90 degrees
            if self.R1P[1] == 90 and self.R2P[1] == 90 and self.R3P[1] == 90:
                flag = False

        flag = True

        while flag:
            # Calculate TARSUS servo position
            self.R1P[2] = self.R1P[2] if self.R1P[2] == 90 else \
                ((self.R1P[2] - self.cycle_gain_pos) if self.R1P[2] > 90 else (self.R1P[2] + self.cycle_gain_pos))
            self.R2P[2] = self.R2P[2] if self.R2P[2] == 90 else \
                ((self.R2P[2] - self.cycle_gain_pos) if self.R2P[2] > 90 else (self.R2P[2] + self.cycle_gain_pos))
            self.R3P[2] = self.R3P[2] if self.R3P[2] == 90 else \
                ((self.R3P[2] - self.cycle_gain_pos) if self.R3P[2] > 90 else (self.R3P[2] + self.cycle_gain_pos))

            # Move COXA
            self.right_side.position(self.R1[1], degrees=self.R1P[1])
            self.right_side.position(self.R2[1], degrees=self.R2P[1])
            self.right_side.position(self.R3[1], degrees=self.R3P[1])

            # Delay for next increment
            sleep_ms(10)

            # Check if every servo is at 90 degrees
            if self.R1P[2] == 90 and self.R2P[2] == 90 and self.R3P[2] == 90:
                flag = False


    def tripod(self, rx=0, ry=0):
        # TODO: ALL THIS SHIT IS FOR THE RIGHT SIDE OF THE HEXAPOD
        # TODO: WRITE CODE FOR THE LEFT SIDE OF THE ROBOT
        # Delay percentage got from joystick
        dRY = float(ry)
        dRX = float(rx)

        # Joystick isn't moved or done walk
        if dRY == 0.0 and dRX == 0.0:
            # Set Hexapod into normal position
            self.return_to_default_position()
            return

        # Check for walking direction for each axis
        directionRY = True if dRY >= 0.0 else False  # True is forward, False is backwards
        directionRX = True if dRX >= 0.0 else False  # True is right, False is left

        # Vertical movement forward (Reference servo - R2C - Right Side Middle COXA)
        if directionRY:
            # Forward cycle
            # In Forward cycle TARSUS position changes only on the R2, L1 and L3
            if self.R2P[0] < 135 and self.t_forward_cycle:
                # Calculate TARSUS position if COXA is half way done (LOWER or RAISE)
                self.R2P[2] = (45 - 90 + self.R2P[0]) if self.R2P[0] >= 90 else (90 + 45 - self.R2P[0])

                # Change COXA servo position
                self.R1P[0] -= self.cycle_gain_pos
                self.R2P[0] += self.cycle_gain_pos
                self.R3P[0] -= self.cycle_gain_pos

                # Move COXA
                self.right_side.position(self.R1[0], degrees=self.R1P[0])
                self.right_side.position(self.R2[0], degrees=self.R2P[0])
                self.right_side.position(self.R3[0], degrees=self.R3P[0])

                # Move TARSUS
                self.right_side.position(self.R1[2], degrees=self.R1P[2])
                self.right_side.position(self.R2[2], degrees=self.R2P[2])
                self.right_side.position(self.R3[2], degrees=self.R3P[2])

                # Check if tripod gait forward cycle is finished (Reference is right side middle COXA)
                if self.R2P[0] == 135:
                    # If yes, then move to backwards cycle
                    self.t_forward_cycle = False

            # Backward cycle
            # In Backward cycle TARSUS position changes only the on R1, R3 and L2
            else:
                # Calculate TARSUS position if COXA is half way done (LOWER or RAISE)
                self.R1P[2] = (45 - 90 + self.R1P[0]) if self.R1P[0] >= 90 else (90 + 45 - self.R1P[0])
                self.R3P[2] = (45 - 90 + self.R1P[0]) if self.R3P[0] >= 90 else (90 + 45 - self.R3P[0])

                # Change COXA servo position
                self.R1P[0] += self.cycle_gain_pos
                self.R2P[0] -= self.cycle_gain_pos
                self.R3P[0] += self.cycle_gain_pos

                # Move COXA
                self.right_side.position(self.R1[0], degrees=self.R1P[0])
                self.right_side.position(self.R2[0], degrees=self.R2P[0])
                self.right_side.position(self.R3[0], degrees=self.R3P[0])

                # Move TARSUS
                self.right_side.position(self.R1[2], degrees=self.R1P[2])
                self.right_side.position(self.R2[2], degrees=self.R2P[2])
                self.right_side.position(self.R3[2], degrees=self.R3P[2])

                # Check if tripod gait backwards cycle is finished (Reference is right side middle COXA)
                if self.R2P[0] == 45:
                    # If yes, then move to forward cycle
                    self.t_forward_cycle = True
        # Vertical movement backwards
        else:
            # Backwards cycle
            if self.R2P[0] > 45 and not self.t_forward_cycle:
                # Calculate TARSUS position if COXA is half way done (LOWER or RAISE)
                self.R2P[2] = (90 - 135 + self.R2P[0]) if self.R2P[0] >= 90 else (45 + 90 - self.R2P[0])

                # Change COXA servo position
                self.R1P[0] += self.cycle_gain_pos
                self.R2P[0] -= self.cycle_gain_pos
                self.R3P[0] += self.cycle_gain_pos

                # Move COXA
                self.right_side.position(self.R1[0], degrees=self.R1P[0])
                self.right_side.position(self.R2[0], degrees=self.R2P[0])
                self.right_side.position(self.R3[0], degrees=self.R3P[0])

                # Move TARSUS
                self.right_side.position(self.R1[2], degrees=self.R1P[2])
                self.right_side.position(self.R2[2], degrees=self.R2P[2])
                self.right_side.position(self.R3[2], degrees=self.R3P[2])

                # Check if tripod gait backwards cycle is finished
                if self.R2P[0] == 45:
                    # If yes, then move to forward cycle
                    self.t_forward_cycle = True

            # Forward cycle
            else:
                # Calculate TARSUS position if COXA is half way done (LOWER or RAISE)
                self.R1P[2] = (90 - 135 + self.R1P[0]) if self.R1P[0] >= 90 else (45 + 90 - self.R1P[0])
                self.R3P[2] = (90 - 135 + self.R3P[0]) if self.R3P[0] >= 90 else (45 + 90 - self.R3P[0])

                # Change COXA servo position
                self.R1P[0] -= self.cycle_gain_pos
                self.R2P[0] += self.cycle_gain_pos
                self.R3P[0] -= self.cycle_gain_pos

                # Move COXA
                self.right_side.position(self.R1[0], degrees=self.R1P[0])
                self.right_side.position(self.R2[0], degrees=self.R2P[0])
                self.right_side.position(self.R3[0], degrees=self.R3P[0])

                # Move TARSUS
                self.right_side.position(self.R1[2], degrees=self.R1P[2])
                self.right_side.position(self.R2[2], degrees=self.R2P[2])
                self.right_side.position(self.R3[2], degrees=self.R3P[2])

                # Check if tripod gait forward cycle is finished
                # If yes, then move to backwards cycle
                if self.R2P[0] == 135:
                    self.t_forward_cycle = False
        """
        # Horizontal movement rightward
        if directionRX:
            # Rightward cycle
            if self.R2P[1] < 120 and self.t_rightward_cycle:
                # Calculate TARSUS position if FEMUR is at half way done in rightward cycle (Raise leg)
                if self.R2P[1] >= 105:
                    self.R2P[2] = 60 - 105 + self.R2P[1]
                # Calculate TARSUS position if FEMUR is less than half way done in rightward cycle (Lower leg)
                else:
                    self.R2P[2] = 105 + 60 - self.R2P[1]

                # Move COXA and TARSUS
                self.right_side.position(self.R2[1], degrees=self.R2P[1])
                self.right_side.position(self.R2[2], degrees=self.R2P[2])

                # Increment servo position
                self.R2P[1] += 1

                # Check if tripod gait rightward cycle is finished
                if self.R2P[1] == 120:
                    # If yes, then move to leftward cycle
                    self.t_rightward_cycle = False

            # Leftward cycle
            else:
                # Move FEMUR Leftward
                self.right_side.position(self.R2[1], degrees=self.R2P[1])

                # Decrement servo position
                self.R2P[1] -= 1

                # Check if tripod gait leftward cycle is finished
                if self.R2P[1] == 90:
                    # If yes, then move to rightward cycle
                    self.t_rightward_cycle = True
        # Horizontal movement leftward
        else:
            # Leftward cycle
            if self.R2P[1] > 60 and not self.t_rightward_cycle:
                # Decrement servo position
                self.R2P[1] -= 1

                # Check if tripod gait rightward cycle is finished
                if self.R2P[1] == 60:
                    # If yes, then move to leftward cycle
                    self.t_rightward_cycle = False

            # Leftward cycle
            else:
                # Calculate TARSUS position if FEMUR is at half way done in leftward cycle (Raise leg)
                if self.R2P[1] <= 75:
                    self.R2P[2] = 105 - 75 + self.R2P[1]
                # Calculate TARSUS position if FEMUR is less than half way done in leftward cycle (Lower leg)
                else:
                    self.R2P[2] = 75 + 105 - self.R2P[1]

                # Move FEMUR and TARSUS
                self.right_side.position(self.R2[1], degrees=self.R2P[1])
                self.right_side.position(self.R2[2], degrees=self.R2P[2])

                # Increment servo position
                self.R2P[1] += 1

                # Check if tripod gait leftward cycle is finished
                if self.R2P[1] == 90:
                    # If yes, then move to rightward cycle
                    self.t_rightward_cycle = True
        """
        # Delay between gait cycles with speed factor got from joystick
        sleep_ms(int(10.0 * (2.0 - abs(max(dRX, dRY)))))

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
            self.L1P[1] -= 1
            self.L2P[1] -= 1
            self.L3P[1] -= 1

            self.R1P[1] -= 1
            self.R2P[1] -= 1
            self.R3P[1] -= 1
        # If False then lower body
        elif not rise and self.L1P[1] < 119:
            # Increment servo position for FEMUR
            self.L1P[1] += 1
            self.L2P[1] += 1
            self.L3P[1] += 1

            self.R1P[1] += 1
            self.R2P[1] += 1
            self.R3P[1] += 1
        # If FEMUR is at max or min servo position, do nothing
        else:
            return

        # Move FEMUR on left side
        self.left_side.position(self.L1[1], degrees=self.L1P[1])
        self.left_side.position(self.L2[1], degrees=self.L2P[1])
        self.left_side.position(self.L3[1], degrees=self.L3P[1])

        # Move FEMUR on right side
        self.right_side.position(self.R1[1], degrees=self.R1P[1])
        self.right_side.position(self.R2[1], degrees=self.R2P[1])
        self.right_side.position(self.R3[1], degrees=self.R3P[1])

        # Delay for next iteration
        #sleep_ms(5)

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
