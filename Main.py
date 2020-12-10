import board #oled tools
import adafruit_ssd1306 #oled screen
import digitalio #oled tools
import Adafruit_ADS1x15 #soil moisture sensor
import os #tools for working with the CLI
import logging #needed for logging
import pigpio #needed for GPIO control
import time #needed for function timing
from pigpio_dht import DHT22 #temp and humidity sensor
from datetime import datetime #needed for logging
from PIL import Image, ImageDraw, ImageFont #oled tools
from CalibrationAndDiagnostics.helpers import * #import helper functions and classes

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

##Create a class for storing menu items within a tree
class menu_tree:
    'This class stores menu options'

    #Create an initalization function for root node
    def __init__(self, option):
        self.option = option #initialize option value
        self.children = [] #intialize empty child list
        self.parent = None #root has no parents (Aww D: )

    #Create a function for adding child nodes
    def add_child(self, child):
        child.parent = self #parent of new instance becomes old instance
        self.children.append(child) #add child instance to list of children

#Begin creation of menu menu tree
root = menu_tree("Main Menu") #Create root node for main menu

Light = menu_tree("Light") #Create child node for light
Light.add_child(menu_tree("Hours")) #Add child node for amount of hours to light
Light.add_child(menu_tree("Time")) #Add child node for time of day to start lighting

root.add_child(Light) #Add child node for light
root.add_child(menu_tree("Water")) #Add a child node for water
root.add_child(menu_tree("Soil")) #Add a child node for soil
root.add_child(menu_tree("Temp")) #Add a child node for temp
root.add_child(menu_tree("Humidity")) #Add a child node for humidity

#Create a function for choosing between menu options
def menu():

    current_option = root #Set initial option to the root option
    position = 0 #set left/right postion
    timer = 0 #start timer

    while timer <= 80: #infinite loop while user is actively choosing
        oled.write_center(current_option.children[position].option) #print the current option to the screen

        if pi.read(BUTTON_ONE) == True :
            if position != 0: #can't have negative postion
                position -= 1 #move one spot to the left
            else:
                position = len(current_option.children)
                timer = 0 #reset timer
        elif pi.read(BUTTON_TWO) == True :
            if len(current_option.children) != 0: #if current option has children
                current_option = current_option.children[position] #set the current option to the first child of the chosen node
                timer = 0 #reset timer
            else: #if the option has no children, it is the final option
                return current_option #and it's node is returned
        elif pi.read(BUTTON_THREE) == True:
            if position < len(current_option.children): #if position is not at the end of the list
                position += 1 #move one spot to the right
            else:
                position = 0 #move position back to other end
            timer = 0 #reset timer
        else:
            timer += 1 #count the timer up

        time.sleep(0.25) #1/4 second delay

choice = menu() #try to run the menu
