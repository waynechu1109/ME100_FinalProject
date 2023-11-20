import machine
import utime

# Define motor control pins for the Cytron Maker Drive
MOTOR_M1A_PIN = machine.PWM(machine.Pin(32))
MOTOR_M1B_PIN = machine.PWM(machine.Pin(14))

# Motor speed (adjusted for safety)
SPEED = 123


def motor_forward():
    MOTOR_M1A_PIN.duty(SPEED)
    MOTOR_M1B_PIN.duty(0)

def motor_backward():
    MOTOR_M1A_PIN.duty(0)
    MOTOR_M1B_PIN.duty(SPEED)

def motor_stop():
    MOTOR_M1A_PIN.duty(0)
    MOTOR_M1B_PIN.duty(0)

# Main loop
while True:
    motor_forward()
    utime.sleep(2)

    motor_backward()
    utime.sleep(2)

    motor_stop()
    utime.sleep(2)