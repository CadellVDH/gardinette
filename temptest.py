import board #oled tools
import adafruit_ssd1306 #oled screen
import digitalio #oled tools
import Adafruit_ADS1x15 #soil moisture sensor
import os #tools for working with the CLI
import logging #needed for logging
import pigpio #needed for GPIO control
import time #needed for function timing
import threading #needed for OLED data continuous updating
import csv #needed for temporary data logging
import config as global_vars #import global variable initialization module
from pigpio_dht import DHT22 #temp and humidity sensor
from datetime import datetime #needed for control timing
from PIL import Image, ImageDraw, ImageFont #oled tools
from CalibrationAndDiagnostics.helpers import * #import helper functions and classes

pins = pinout()
TEMP = pins.getPin('TEMP')
dht = DHT22(TEMP)

while True:
    result = dht.read()
    temp = result["temp_f"]
    hum = result["humidity"]
    print(temp)
    print(hum)
