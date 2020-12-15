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

#Begin creation of menu tree
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
    position = 0 #set left/right position
    timer = 0 #start timer

    while timer <= 80: #infinite loop while user is actively choosing
        oled.write_center(current_option.children[position].option) #print the current option to the screen
        oled.write("<--", 0, oled.height/2, clear=False) #create left arrow
        oled.write("-->", oled.width-18, oled.height/2, clear=False) #create right arrow

        if pi.read(BUTTON_ONE) == True :
            if position != 0: #can't have negative position
                position -= 1 #move one spot to the left
            else:
                position = len(current_option.children)-1
                timer = 0 #reset timer
        elif pi.read(BUTTON_TWO) == True :
            if current_option.children:
                current_option = current_option.children[position] #set the current option to the first child of the chosen node
            if current_option.children: #if current option has children
                timer = 0 #reset timer
            else: #if the option has no children, it is the final option
                break
        elif pi.read(BUTTON_THREE) == True:
            if position < len(current_option.children)-1: #if position is not at the end of the list
                position += 1 #move one spot to the right
            else:
                position = 0 #move position back to other end
            timer = 0 #reset timer
        else:
            timer += 1 #count the timer up

        time.sleep(.25) #1/4 second delay

    return current_option #and it's node is returned

#Create a function for choosing paramater values
def param_adjust(choice_list, unit=""):
    timer = 0 #create a timer
    position = 0 #start at position 0

    while timer <= 160: #while elapsed time is less than 20 seonds
        oled.write_center(str(choice_list[position])) #print the current choice to the OLED
        oled.write(unit, oled.width/2, 10, clear=False) #write the unit above the number
        oled.write("<--", 0, oled.height/2, clear=False) #create left arrow
        oled.write("-->", oled.width-18, oled.height/2, clear=False) #create right arrow

        if pi.read(BUTTON_ONE):
            if position != 0:
                position -= 1 #move left
            else:
                position = len(choice_list) - 1 #otherwise go to end of choice_list

            timer = 0 #reset timer
        elif pi.read(BUTTON_TWO):
            break
        elif pi.read(BUTTON_THREE):
            if position < len(choice_list)-1: #if position is not at end of list
                position += 1 #move right
            else:
                position = 0 #move back to beginning
        else:
            timer += 1 #count the timer up

        time.sleep(.125) #1/4 second delay

    return choice_list[position] #return the chosen value

#Create a function for the use to adjust box parameters
def param_select():
    menu_choice = menu() #call the menu function to find out what parameter the user wants to adjust

    if menu_choice.option == "Hours":
        allowed = list(range(1, 24)) #list is 1-24
        return param_adjust(allowed, "Hours")
    elif menu_choice.option == "Time":
        allowed = [] #empty list
        for i in range(1, 24): #generate list
            for j in range(1, 59):
                if j < 10:
                    allowed[i*j] = "{}:0{}".format(i,j) #make list with 0 in front of minute if minute < 10
                else:
                    allowed[i*j] = "{}:{}".format(i,j) #otherwise make list using only the minute
        return param_adjust(allowed)
    elif menu_choice.option == "Water":
        allowed = [] #empty list
        for i in range(1, 24): #generate list
            for j in range(1, 59):
                if j < 10:
                    allowed[i*j] = "{}:0{}".format(i,j) #make list with 0 in front of minute if minute < 10
                else:
                    allowed[i*j] = "{}:{}".format(i,j) #otherwise make list using only the minute
        return param_adjust(allowed)
    elif menu_choice.option ==  "Soil":
        allowed = list(range(20, 80)) #create list of allowed soil moistures
        return param_adjust(allowed, "%")
    elif menu_choice.option == "Temp":
        allowed = list(range(60, 90)) #create list of allowed temps
        return param_adjust(allowed, "F")
    elif menu_choice.option == "Humidity":
        allowed = list(range(10, 90)) #create list of allowed humidities
        return param_adjust(allowed, "%")
    else:
        return NULL

print(param_select())
