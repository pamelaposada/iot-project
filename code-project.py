# import relevant modules
import mraa
import time
import subprocess
import platform
from TH02 import TH02
from Servo import *

# led light blinking on and off
led = mraa.Gpio(13)
led.dir(mraa.DIR_OUT)
led.write(1)
time.sleep(1)
led.write(0)
time.sleep(1)
print("Motherboard LED has flashed")

# sensors
# light sensor is connected to analog port 2
lightSensor = mraa.Aio(2)

# UV sensor is connected to analog port 1
uvSensor = mraa.Aio(1)

# Soil (Moisture) sensor is connected to analog port 0
soilSensor = mraa.Aio(0)

# Temperature and Humidity Sensor is connected to I2C
THSensor = TH02()

# Servo is connected to digital port 5
myServo = Servo("First Servo")
myServo.attach(5)

# Relay is connected
relay = mraa.Gpio(5)
relay.dir(mraa.DIR_OUT)

while True:

    # Read light sensor
    lights = str(lightSensor.read())

    # Read UV sensor
    uv = str(uvSensor.read())

    # Read mositure sensor
    soil = str(soilSensor.read())

    # Read mositure sensor
    tmp = str(round(THSensor.getTemperature(), 1))
    hum = str(round(THSensor.getHumidity(), 1))

    # priting the values on the screen
    print("Temp=" + tmp + " Humidity=" + hum)
    print("light: ", lights)
    print("uv: ", uv)
    print("soil: ", soil)

    # finding the weather and determining the angle for shade
    if THSensor.getTemperature() <= 10:
        weather = 'cold'
        arg = 0
    elif THSensor.getTemperature() <= 20:
        weather = 'medium'
        arg = 30
    elif THSensor.getTemperature() <= 30:
        weather = 'hot'
        arg = 60
    else:
        weather = 'superhot'
        arg = 120

    # moving the servo with correct angle based on the weather
    myServo.write(arg)

    # printing the servo movement angle
    print("Servo Arm moved to " + str(myServo.read()) + " degrees.")
    arg = str(arg)

    # turning on the motor if the soil level is less than 10
    if soil < 10:
        relay.write(1)

    print("motor on")

    # Sending the logs to splunk server for every one minute
    cmd_str = 'logger --udp --port 51514 --server splunkhome.myddns.me IoTid='
    cmd_str = cmd_str + platform.node() + ' light=' + lights + ' UV=' + uv + \
        ' Soil=' + soil + ' Temp=' + tmp + ' Hum=' + hum + ' Servo=' + arg
    subprocess.call(cmd_str, shell=True)
    # print("logged", platform.node())
    time.sleep(60)
