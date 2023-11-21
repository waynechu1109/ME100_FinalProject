import machine
import utime

# Define motor control pins for the Cytron Maker Drive
MOTOR_M1A_PIN = machine.PWM(machine.Pin(32))
MOTOR_M1B_PIN = machine.PWM(machine.Pin(14))

MOTOR_M2A_PIN = machine.PWM(machine.Pin(4))
MOTOR_M2B_PIN = machine.PWM(machine.Pin(5))

# Motor speed (adjusted for safety)
SPEED = 223


def motor1_forward():
    MOTOR_M1A_PIN.duty(SPEED)
    MOTOR_M1B_PIN.duty(0)

def motor1_backward():
    MOTOR_M1A_PIN.duty(0)
    MOTOR_M1B_PIN.duty(SPEED)

def motor1_stop():
    MOTOR_M1A_PIN.duty(0)
    MOTOR_M1B_PIN.duty(0)
    
def motor2_forward():
    MOTOR_M2A_PIN.duty(SPEED)
    MOTOR_M2B_PIN.duty(0)

def motor2_backward():
    MOTOR_M2A_PIN.duty(0)
    MOTOR_M2B_PIN.duty(SPEED)

def motor2_stop():
    MOTOR_M2A_PIN.duty(0)
    MOTOR_M2B_PIN.duty(0)

# Main loop
while True:
    motor2_forward()
    motor1_forward()
    utime.sleep(2)

    motor1_backward()
    motor2_forward()
    utime.sleep(2)

    motor1_stop()
    motor2_stop()
    utime.sleep(2)