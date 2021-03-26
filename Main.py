import board #oled tools
import adafruit_ssd1306 #oled screen
import digitalio #oled tools
import Adafruit_ADS1x15 #soil moisture sensor
import os #tools for working with the CLI
import logging #needed for logging
import pigpio #needed for GPIO control
import time #needed for function timing
import config as global_vars #import global variable initialization module
from pigpio_dht import DHT22 #temp and humidity sensor
from datetime import datetime #needed for logging
from PIL import Image, ImageDraw, ImageFont #oled tools
from CalibrationAndDiagnostics.helpers import * #import helper functions and classes
from Core_Functions import * #import core functions and classes

pins = pinout() #initialize pinout
oled = oled_utility(128, 32, pins.getAddr('OLED')) #initialize OLED display
pi = pigpio.pi() #Initialize pigpio

#Create constants for all pin numbers
FAN_ONE = pins.getPin('FAN_ONE')
FAN_TWO = pins.getPin('FAN_TWO')
PUMP = pins.getPin('PUMP')
LIGHT = pins.getPin('LIGHT')
FLOAT = pins.getPin('FLOAT')
TEMP = pins.getPin('TEMP')
BUTTON_ONE = pins.getPin('BUTTON_ONE')
BUTTON_TWO = pins.getPin('BUTTON_TWO')
BUTTON_THREE = pins.getPin('BUTTON_THREE')

#Set all pin modes
pi.set_mode(FAN_ONE, pigpio.OUTPUT)
pi.set_mode(FAN_TWO, pigpio.OUTPUT)
pi.set_mode(PUMP, pigpio.OUTPUT)
pi.set_mode(LIGHT, pigpio.OUTPUT)
pi.set_mode(FLOAT, pigpio.INPUT)
pi.set_mode(BUTTON_ONE, pigpio.INPUT)
pi.set_mode(BUTTON_TWO, pigpio.INPUT)
pi.set_mode(BUTTON_THREE, pigpio.INPUT)

#Set needed internal pull down resistors
pi.set_pull_up_down(BUTTON_ONE, pigpio.PUD_DOWN)
pi.set_pull_up_down(BUTTON_TWO, pigpio.PUD_DOWN)
pi.set_pull_up_down(BUTTON_THREE, pigpio.PUD_DOWN)

targets = target() #initialize target setting class

dataDisplay = dataGlance() #initialize data glance object
dataDisplay.start() #start data quick display

#Initialize DHT 22
DHT_SENSOR = DHT22(TEMP)

while True: #begin main control loop
    #Get current sensor values
    try:
        [global_vars.current_temp, global_vars.current_humidity] = getTempHumidity(DHT_SENSOR)
        global_vars.current_soil = getSoilMoisture()
    except Exception as e:
        logging.error("Failed one or more sensor readings: %s" % e) #exception block to prevent total failure if any sensor fails a reading
