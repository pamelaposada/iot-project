# import relevant modultmphumes
import subprocess
import time
import os
import sys
import platform
from TH02 import TH02
from Servo import *
from I2cLCDRGBBacklight import I2cLCDDisplay  # LCD library

# led light blinking on and off
led = mraa.Gpio(13)
led.dir(mraa.DIR_OUT)

# light, uv, soil, and TH02 sensor
lightSensor = mraa.Aio(2)
uvSensor = mraa.Aio(1)
soilSensor = mraa.Aio(0)
THSensor = TH02()

# Servo is connected to digital port 5
myServo = Servo("First Servo")
myServo.attach(5)

# Relay is connected
relay = mraa.Gpio(5)
relay.dir(mraa.DIR_OUT)

# Starting loop
counter = 0
while True:
    # count how many times the script has runned
    counter += 1

    # Led flashing
    led.write(1)
    time.sleep(1)
    led.write(0)
    time.sleep(1)
    print("Motherboard LED has flashed for " + str(counter) + " times")

    lights = str(lightSensor.read())
    uv = str(uvSensor.read())
    soil = str(soilSensor.read())
    tmp = round(THSensor.getTemperature(), 1)
    hum = round(THSensor.getHumidity(), 1)
    print("Temp=" + str(tmp) + " Humidity=" + str(hum))
    print("light: ", lights)
    print("uv: ", uv)
    print("soil: ", soil)

    # Classify humidity levels
    if int(hum) <= 55:
        humdescription = "dry"
    elif int(hum) > 55 and int(hum) < 80:
        humdescription = "sticky"
    elif int(hum) >= 80:
        humdescription = "very humid"

    # checking the temp and moving the servo with correct angle based on the temp
    if THSensor.getTemperature() <= 15 and THSensor.getTemperature() > -20:
        weather = 'cold'
        arg = 0
    elif THSensor.getTemperature() <= 25 and THSensor.getTemperature() > 15:
        weather = 'warm'
        arg = 30
    elif THSensor.getTemperature() <= 35 and THSensor.getTemperature() > 25:
        weather = 'hot'
        arg = 60
    elif THSensor.getTemperature() <= 50 and THSensor.getTemperature() > 35:
        weather = 'superhot'
        arg = 120

    # Calling I2cLCDDisplay module ------
    LCD = I2cLCDDisplay()
    LCD.I2cLCDLEDInit()

    # change LED color based on temperature
    if weather == 'cold':
        LCD.LEDColor(0, 0, 255)
    elif weather == 'warm':
        LCD.LEDColor(70, 192, 103)
    elif weather == 'hot':
        LCD.LEDColor(204, 102, 0)
    elif weather == 'superhot':
        LCD.LEDColor(204, 0, 0)

    messg1 = "Current environment temperature: " + str(tmp) + " degrees"
    messg2 = "It is " + weather + " and " + humdescription + " here!"
    LCD.LCDPrint(messg1)
    LCD.LCDInstruction(0x80+0x28)
    LCD.LCDPrint(messg2)
    print(messg1 + ". " + messg2)

    # Calling Servo module -----
    myServo.write(arg)
    print("Servo Arm moved to " + str(myServo.read()) + " degrees.")

    # turning on the motor if the soil level is less than 10
    if soil < 10:
        relay.write(1)
        relaystate = 'on'
    else:
        relaystate = 'off'
    print("motor " + relaystate)

    # Sending the logs to splunk server for every one minute
    cmd_str = 'logger --udp --port 51514 --server splunkhome.myddns.me IoTid='
    cmd_str = cmd_str + platform.node() + ' light=' + lights + ' UV=' + uv + ' Soil=' + soil + \
        ' Temp=' + str(tmp) + ' Hum=' + str(hum) + ' Servo=' + \
        str(arg) + ' Relay=' + relaystate
    subprocess.call(cmd_str, shell=True)
    print("logged", platform.node())

    # count script
    print("The script ran " + str(counter) + " times.")

    # stop for X seconds
    time.sleep(600)
