# This file is executed on every boot (including wake-boot from deepsleep)
import esp
import network
import time
import machine

#esp.osdebug(None)
print('running boot')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
password = '6Exz)Cs3'

# attempt to connect 20 times
# print a fail message or a success message
if wlan.isconnected():
    print('connected')
    wlan.disconnect()
    
if not wlan.isconnected():
    print('connecting to network...')
    # you can connect to other networks by editing the next line with suitable network_name and password
    #wlan.disconnect()
    wlan.connect('Berkeley-IoT', password) 

    tries = 0
    while not wlan.isconnected() and tries < 30:
        print('...')
        wlan.connect('Berkeley-IoT', password)

        time.sleep(1)
        tries = tries + 1
    print('network config:', wlan.ifconfig())
    
    
    if wlan.isconnected():
        print("WiFi connected at", wlan.ifconfig()[0])
    else:
        print("Mission failed")
        
        

# print current date and time using real-time clock
from machine import RTC

print("inquire RTC time")

rtc = machine.RTC()
rtc.datetime()
print(rtc.datetime())