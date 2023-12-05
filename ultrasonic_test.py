from umqtt.simple import MQTTClient
from machine import Pin, time_pulse_us, PWM, Timer
import time
from time import sleep
import math
import uasyncio as asyncio
import network
import sys
import machine
import utime
import umqtt1

# check wifi connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
ip = wlan.ifconfig()[0]
if ip == '0.0.0.0':
    print("no wifi connection")
    sys.exit()
else:
    print("connected to WiFi at IP", ip)

# Set up Adafruit connection
myMqttClient = "TestClient"
adafruitIoUrl = "io.adafruit.com"

# CHANGE HERE
adafruitUsername = "Bensons"
adafruitAioKey = "aio_faVI67atIeI3Mj8siN3VwwjMXoHH"

# Connect to Adafruit server
print("Connecting to Adafruit")
mqtt_adafruit = umqtt1.MQTTClient(myMqttClient, adafruitIoUrl, 0,
                                  adafruitUsername, adafruitAioKey)
time.sleep(0.5)
mqtt_adafruit.connect()
print("Connected!")

# CHANGE HERE
feedName = "Bensons/feeds/benshu-cao"

# Set up MQTT connection
# Important: change the line below to a unique string,
# e.g. your name & make corresponding change in mqtt_plot_host.py
session = 'benshu/esp32/helloworld'
BROKER = 'broker.hivemq.com'

# connect to MQTT broker
print("Connecting to MQTT broker", BROKER, "...", end="")
mqtt = MQTTClient(client_id="esp32", server=BROKER, port=1883)
mqtt.connect()
print("Connected!")

# Define motor control pins for the Cytron Maker Drive
MOTOR_M1A_PIN = machine.PWM(machine.Pin(32))
MOTOR_M1B_PIN = machine.PWM(machine.Pin(14))

MOTOR_M2A_PIN = machine.PWM(machine.Pin(4))
MOTOR_M2B_PIN = machine.PWM(machine.Pin(5))

# Motor speed (adjusted for safety)
SPEED = 200

# Pin numbers for ESP32 (adjust as needed)
sensor_1_trigger = 26  # GPIO5 for trigger
sensor_1_echo = 25     # GPIO4 for echo

sensor_2_trigger = 27
sensor_2_echo = 33

t1 = Timer(1)

LED = 12
BUZ = 15

buz = Pin(BUZ, mode=Pin.OUT)
duty_cycle = 100
L1 = PWM(buz,freq=500,duty=duty_cycle)

music = [20]
rest = [1]

dist_arr = [[0, 0], [0, 0]]
period = 0.1
i = [0, 0]
activate = False

# trigger = Pin(sensor_1_trigger, Pin.OUT)
# echo = Pin(sensor_1_echo, Pin.IN)
led = Pin(LED, mode=Pin.OUT)

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

note_index = 0
# This is the callback function
def tcb(timer):
    global duty_cycle
    global note_index
    global activate

    if activate:
#         for i in range(3):
        L1.freq(music[0])
    else:
        L1.freq(rest[0])


def distance(label):
    if label == 1:
        trigger = Pin(sensor_1_trigger, Pin.OUT)
        echo = Pin(sensor_1_echo, Pin.IN)
    elif label == 2:
        trigger = Pin(sensor_2_trigger, Pin.OUT)
        echo = Pin(sensor_2_echo, Pin.IN)
        
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

def response():
    global t1
    led_period = 0.5
#     buz_period = led_period*1000
    
    t1.init(period=500, mode=t1.PERIODIC, callback=tcb) # buzzer on
    
    for _ in range(5):  # light LED and drive motors
        
        
        motor2_stop()
        motor1_stop()
        led.value(1)
        time.sleep(led_period)       
                
        motor2_stop()
        motor1_stop()
        led.value(0)
        time.sleep(led_period)
        
def detect(label):
    global dist_arr_1, period, i, activate

    dist_1 = distance(label)
#   print("Measured Distance = %.1f cm" % dist)
    dist_arr[label-1][1] = dist_arr[label-1][0]
    dist_arr[label-1][0] = dist_1
    if (dist_arr[label-1][0] is not 0) and (dist_arr[label-1][1] is not 0):
        velo = (dist_arr[label-1][0]-dist_arr[label-1][1])/period
        if math.fabs(velo) >= 10: # the absolute value of the velo
            i[label-1] += 1
        else:
            i[label-1] = 0
        
        if i[label-1] == 5:
            activate = True
            return
        
        print("Label:", label, "Measured Velocity = %.1f cm/s" % velo)
    time.sleep(period)    

if __name__ == '__main__':

    direction_index = 0
    
    while True:
        if direction_index == 4:
            direction_index = 0
            motor1_forward()
            motor2_backward()
        elif 0 <= direction_index and direction_index <= 1:
            motor1_forward()
            motor2_backward()
        else:
            motor1_backward()
            motor2_forward()
            
        L1.freq(1)
        detect(1)
        detect(2)
            
        if activate:
            print('ACTIVATE!')
            topic = "{}/data".format(session)
            data = "{}".format("WARNING!!!")
            print("send topic='{}' data='{}'".format(topic, data))
            mqtt.publish(topic, data)
            mqtt_adafruit.publish(feedName,"WARNING!!!(adafruit)")
            print("Published {} to {}.".format("WARNING!!!(adafruit)",feedName))
            response()
            activate = False
            L1.freq(1)
            i[0] = 0 # label for motion continuity
            i[1] = 0
            
        direction_index += 1
        
        