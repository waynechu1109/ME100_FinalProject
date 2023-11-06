from machine import Pin, time_pulse_us
import time
import math

# Pin numbers for ESP32 (adjust as needed)
GPIO_TRIGGER = 26  # GPIO5 for trigger
GPIO_ECHO = 25     # GPIO4 for echo

trigger = Pin(GPIO_TRIGGER, Pin.OUT)
echo = Pin(GPIO_ECHO, Pin.IN)

def distance():
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)
    
    while echo.value() == 0:
        pulse_start = time.ticks_us()
    
    while echo.value() == 1:
        pulse_end = time.ticks_us()
    
    pulse_duration = time.ticks_diff(pulse_end, pulse_start)
    distance = (pulse_duration * 0.0343) / 2  # Speed of sound in air is approximately 343 m/s

    return distance


dist_arr = [0, 0]
period = 0.1

if __name__ == '__main__':
    try:
        while True:
            dist = distance()
#             print("Measured Distance = %.1f cm" % dist)
            dist_arr[1] = dist_arr[0]
            dist_arr[0] = dist
            if (dist_arr[0] is not 0) and (dist_arr[1] is not 0):
                velo = (dist_arr[0]-dist_arr[1])/period
                print("Measured Velocity = %.1f cm/s" % velo)
            time.sleep(period)
 
    except KeyboardInterrupt:
        print("Measurement stopped by User")
