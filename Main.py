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
pi.set_pull_up_down(FLOAT, pigpio.PUD_DOWN)

dataCollectThread = dataCollect(TEMP, FLOAT) #initialize data collect object
dataCollectThread.start() #begin running the data collection thread

dataGlanceThread = dataGlance() #initialize data glance object
dataGlanceThread.start() #start data quick display

pumpControlThread = pumpControl(PUMP) #intialize pumpControl object
pumpControlThread.start() #start pumpControl thread

targetAdjustThread = targetAdjust() #initialize target adjustment thread

while True: #begin main control loop
    #Check if any button has been pressed and wake to menu screen
    if pi.read(BUTTON_ONE) == True or pi.read(BUTTON_TWO) == True or pi.read(BUTTON_THREE) == True or True:
        if dataGlanceThread.isAlive() == True:
            global_vars.data_glance_exit_flag = True #if data glance is running, kill it
        time.sleep(0.1) #delay for cleanup
        #Try starting the thread, if there is a runtime error due to thread being used already, delete the old instance and start a new one
        try:
            targetAdjustThread.start() #start targetAdjust thread
        except RuntimeError:

            targetAdjustThread = targetAdjust() #initialize target adjustment thread
            targetAdjustThread.start() #start targetAdjust thread


    #Check if threads are alive and restart them if they have stopped
    if dataCollectThread.isAlive() == False:
        del pumpControlThread
        dataCollectThread = dataCollect(TEMP, FLOAT) #initialize data collect object
        dataCollectThread.start()
    # if pumpControlThread.isAlive() == False:
    #     del pumpControlThread
    #     pumpControlThread = pumpControl(PUMP) #intialize pumpControl object
    #     pumpControlThread.start()
    if dataGlanceThread.isAlive() == False and targetAdjustThread.isAlive() == False:
        global_vars.data_glance_exit_flag = False
        del dataGlanceThread
        dataGlanceThread = dataGlance() #initialize data glance object
        dataGlanceThread.start()

    time.sleep(0.2) #delay to prevent button bouncing
