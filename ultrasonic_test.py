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

LED = 12
BUZ = 15

buz = Pin(BUZ, mode=Pin.OUT)
duty_cycle = 100
L1 = PWM(buz,freq=500,duty=duty_cycle)

# various notes and pitches
C3 = 131
CS3 = 139
D3 = 147
DS3 = 156
E3 = 165
F3 = 175
FS3 = 185
G3 = 196
GS3 = 208
A3 = 220
AS3 = 233
B3 = 247
C4 = 262
CS4 = 277
D4 = 294
DS4 = 311
E4 = 330
F4 = 349
FS4 = 370
G4 = 392
GS4 = 415
A4 = 440
AS4 = 466
B4 = 494
C5 = 523
CS5 = 554
D5 = 587
DS5 = 622
E5 = 659
F5 = 698
FS5 = 740
G5 = 784
GS5 = 831
A5 = 880
AS5 = 932
B5 = 988
C6 = 1047
CS6 = 1109
D6 = 1175
DS6 = 1245
E6 = 1319
F6 = 1397
FS6 = 1480
G6 = 1568
GS6 = 1661
A6 = 1760
AS6 = 1865
B6 = 1976
C7 = 2093
CS7 = 2217
D7 = 2349
DS7 = 2489
E7 = 2637
F7 = 2794
FS7 = 2960
G7 = 3136
GS7 = 3322
A7 = 3520
AS7 = 3729
B7 = 3951
C8 = 4186
CS8 = 4435
D8 = 4699
DS8 = 4978

music = [G5]
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
    if note_index < len(music)-1:
        note_index += 1
    else:
        note_index = 0
    
    L1.freq(music[note_index])

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
    led_period = 0.5
    buz_period = led_period*1000
    for _ in range(5):
        
        led.value(1)
        time.sleep(led_period)
        
        t1 = Timer(1)
        t1.init(period=500, mode=t1.PERIODIC, callback=tcb)
        
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
            L1.freq(1)
            i[0] = 0
            i[1] = 0
