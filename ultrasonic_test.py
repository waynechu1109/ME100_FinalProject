from umqtt.simple import MQTTClient
from machine import Pin, time_pulse_us, PWM, Timer
import time
from time import sleep
import math
import uasyncio as asyncio
import network
import sys

# Important: change the line below to a unique string,
# e.g. your name & make corresponding change in mqtt_plot_host.py
session = 'benshu/esp32/helloworld'
BROKER = 'broker.hivemq.com'

# check wifi connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
ip = wlan.ifconfig()[0]
if ip == '0.0.0.0':
    print("no wifi connection")
    sys.exit()
else:
    print("connected to WiFi at IP", ip)

# connect to MQTT broker
print("Connecting to MQTT broker", BROKER, "...", end="")
mqtt = MQTTClient(client_id="esp32", server=BROKER, port=1883)
mqtt.connect()
print("Connected!")


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

music = [131]
rest = [1]

dist_arr = [[0, 0], [0, 0]]
period = 0.1
i = [0, 0]
activate = False

# trigger = Pin(sensor_1_trigger, Pin.OUT)
# echo = Pin(sensor_1_echo, Pin.IN)
led = Pin(LED, mode=Pin.OUT)

note_index = 0
# This is the callback function
def tcb(timer):
    global duty_cycle
    global note_index
    global activate

    if activate:
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

def blinking_led():
    global t1
    led_period = 0.5
#     buz_period = led_period*1000
    
    t1.init(period=500, mode=t1.PERIODIC, callback=tcb) # buzzer on
    
    for _ in range(5):
        
        led.value(1)
        time.sleep(led_period)       
                
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
        if math.fabs(velo) >= 5: # the absolute value of the velo
            i[label-1] += 1
        else:
            i[label-1] = 0
        
        if i[label-1] == 10:
            activate = True
            return
        
        print("Label:", label, "Measured Velocity = %.1f cm/s" % velo)
    time.sleep(period)    

if __name__ == '__main__':

    while True:
        L1.freq(1)
        detect(1)
        detect(2)
            
        if activate:
            print('ACTIVATE!')
            topic = "{}/data".format(session)
            data = "{}".format("WARNING!!!")
            print("send topic='{}' data='{}'".format(topic, data))
            mqtt.publish(topic, data)
            blinking_led()
            activate = False
#             t1.stop()
            L1.freq(1)
            i[0] = 0 # label for motion continuity
            i[1] = 0
