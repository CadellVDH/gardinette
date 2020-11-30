import board #oled tools
import adafruit_ssd1306 #oled screen
import digitalio #oled tools
import Adafruit_ADS1x15 #soil moisture sensor
import os #tools for working with the CLI
import logging #needed for logging
import pigpio #needed for GPIO control
import time #needed for function timing
from pigpio_dht import DHT22 #temp and humidity sensor
from configparser import ConfigParser #ini file manipulation
from datetime import datetime #needed for logging
from PIL import Image, ImageDraw, ImageFont #oled tools
from helpers import adc_read, easy_input, pinout #import helper functions and classes

#The purpose of this script is to ensure that all peripheral hardware
#components are connected and functioning properly, prior to startup
#as well as during troubleshooting

#Initialize all pins
pins = pinout()

#Get current directory for log files and for pin file
PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
PATH = "%s/Pinout.ini" % PROJECT_DIRECTORY

#Open a log file to save diagnostic data
TODAY = datetime.now()
LOG_FILE = "%s/Logs/" % PROJECT_DIRECTORY + TODAY.strftime("%d-%m-%y-%H:%M") #name log file based on date and time
if (os.path.isdir("%s/Logs/" % PROJECT_DIRECTORY) == False): #check if log directory already exists
    os.mkdir("%s/Logs/" % PROJECT_DIRECTORY) #make one if it doesnt
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, filemode='w') #make a log file with a name based on the current date and time

#Begin hardware diagnostics

#First test the OLED screen
print("Now testing the OLED screen...\n")
try: #attempt to detect the OLED
    print("Attempting to detect OLED...\n")
    oled_reset = digitalio.DigitalInOut(board.D4) #reset oled
    i2c = board.I2C() #these next few lines initialize the OLED
    oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=pins.getAddr('OLED'),reset=oled_reset) #specify oled we're using
    print("OLED detected\n")
    logging.debug("OLED detected") #log results
except Exception as e:
    print("Error occured while detecting board\n") #throw error if one occurs
    logging.error("Error detecting OLED: %s" % e) #log results

try: #attempt to clear the OLED
    print("Attempting to clear the OLED...\n")
    oled.fill(0) #clear display
    oled.show() #update the display
    print("OLED cleared\n")
    logging.debug("OLED cleared") #log results
except Exception as e:
    print("Error occured while clearing OLED\n") #throw error if one occurs
    logging.error("Error clearing OLED: %s" % e) #log results

try: #attempt to write to the oled
    print("Attempting to write to OLED...\n")
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=0)
    text = "Gardinette!"
    (font_width, font_height) = font.getsize(text)
    draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),text,font=font,fill=255)
    oled.image(image)
    oled.show() #print image to OLED
    logging.debug("All functions for writing to the OLED executed succesffully") #log results
except Exception as e:
    print("Error occured while writing text to the OLED\n")
    logging.error("Error, some functions failed to execute while writing to the OLED: %s" % e) #log results

if (easy_input('Was the text "Gardinette!" shown on the display?') == False): #verify real world
    print("Error occured while writing to OLED screen\n")
    logging.error("Error, OLED hardware seems to have failed") #log results
else:
    print("OLED tests have succeeded\n")
    logging.debug("OLED hardware is operational") #log results

print("All OLED tests have been completed\n")

#Next test the ADC/moisture sensor
print("Now testing the ADC/Moisture Sensor\n")

print("Attempting to read value from ADC\n")
try:
    ADCvalue = adc_read(retry=5)
    print("ADC value: %f\n" % ADCvalue) #print ADC value to console
    print("ADC succesffully read\n")
    logging.debug("ADC succesffully read") #log results
except Exception as e:
    print("Error occured while reading ADC value\n")
    logging.error("Error occured while reading ADC: %s" % e) #log results

print("All ADC tests have been completed\n")

#Test the temperature and humidity sensor
print("Now testing the temperature and humidity sensor\n")
DHT_SENSOR = DHT22(pins.getPin('TEMP')) #instantiate DHT sensor

try:
    result = DHT_SENSOR.sample(samples=3) #attempt to read temp and humidity sensor
    temperature = result["temp_f"] #get temp separately in F
    humidity = result["humidity"] #get humidity separately
    print("Temp: %f\n" % temperature) #print temperature to console
    print("Humidity: %f\n" % humidity) #print humidity to console
    print("Temp and humidity tests have succeeded\n")
    logging.debug("Temp and humidity tests have succeeded") #log results
except Exception as e:
    print("An error occured while reading the temperature or humidity\n")
    logging.error("Error, Temp and humidity sensor failed to read: %s" % e)

print("All temperature and humidity tests have been completed\n")

#Test both fans
print("Now testing the ventilation fans")

try: #test if fan one turns on
    print("Checking if fan one turns on\n")
    pi = pigpio.pi() #create instance of pigpio.pi class
    pi.set_mode(pins.getPin('FAN_ONE'), pigpio.OUTPUT) #set fan one to output

    pi.write(pins.getPin('FAN_ONE'), 1) #set fan one GPIO to high
    if (easy_input('Did fan one turn on?') == False): #verify real world
        print("Error occured while turning fan one on\n")
        logging.error("Error, fan hardware seems to have failed") #log results
    else:
        pi.write(pins.getPin('FAN_ONE'), 0) #turn fan one back off
        logging.debug("Fan one turns on") #log results
except Exception as e:
    print("Error occured while turning fan one on\n")
    logging.error("Error, failed to write to fan one GPIO: %s" % e)

try: #test if fan two turns on
    print("Checking if fan two turns on\n")
    pi.set_mode(pins.getPin('FAN_TWO'), pigpio.OUTPUT) #set fan two to output

    pi.write(pins.getPin('FAN_TWO'), 1) #set fan two GPIO to high
    if (easy_input('Did fan two turn on?') == False): #verify real world
        print("Error occured while turning fan two on\n")
        logging.error("Error, fan hardware seems to have failed") #log results
    else:
        pi.write(pins.getPin('FAN_TWO'), 0) #turn fan two back off
        logging.debug("Fan two turns on") #log results
except Exception as e:
    print("Error occured while turning fan two on\n")
    logging.error("Error, failed to write to fan two GPIO: %s" % e)

input("Please wait until both fans have stopped, then press [Enter]...")

try: #test if fan one works with PWM
    print("Checking if fan one speed control works\n")
    pi = pigpio.pi() #create instance of pigpio.pi class

    pi.set_PWM_dutycycle(pins.getPin('FAN_ONE'), 128) #set fan one GPIO 50% PWM
    if (easy_input('Did fan one turn on?') == False): #verify real world
        print("Error occured while turning fan one on\n")
        logging.error("Error, fan hardware seems to have failed") #log results
    else:
        pi.set_PWM_dutycycle(pins.getPin('FAN_ONE'), 0) #turn fan one back off
        logging.debug("Fan one turns on") #log results
except Exception as e:
    print("Error occured while turning fan one on\n")
    logging.error("Error, failed to write to fan one GPIO: %s" % e)

try: #test if fan two works with PWM
    print("checking if fan two speed control works\n")

    pi.set_PWM_dutycycle(pins.getPin('FAN_TWO'), 128) #set fan two GPIO 50% PWM
    if (easy_input('Did fan two turn on?') == False): #verify real world
        print("Error occured while turning fan two on\n")
        logging.error("Error, fan hardware seems to have failed") #log results
    else:
        pi.set_PWM_dutycycle(pins.getPin('FAN_TWO'), 0) #turn fan two back off
        logging.debug("Fan two turns on") #log results
except Exception as e:
    print("Error occured while turning fan two on\n")
    logging.error("Error, failed to write to fan two GPIO: %s" % e)

print("Fan tests have been completed\n")

#Test the float sensor
print("Now testing the float sensor\n")
Float_Actual = easy_input('Is the float sensor floating?') #verify real world

try:
    print("Now attempting to read float sensor...")
    pi.set_mode(pins.getPin('FLOAT'), pigpio.INPUT) #set float sensor to input
    pi.set_pull_up_down(pins.getPin('FLOAT'), pigpio.PUD_DOWN) #set internal pull down resistor
    Float_Read = pi.read(pins.getPin('FLOAT')) #read float sensor value

    if (Float_Read == Float_Actual): #check if float sensor value agrees with reality
        print("Float sensor succesffully read\n")
        logging.debug("Float sensor succesffully read")
    else:
        print("Float sensor failed to read\n")
        logging.error("Float sensor hardware does not agree with reality")
except Exception as e:
    print("Error occured while reading float sensor\n")
    logging.error("Error, failed to read float sensor: %s" % e)


#Test the pump
print("Now testing the pump\n")
try:
    if (Float_Actual == 1): #check if it's safe to pump
        pi.write(pins.getPin('PUMP'), 1) #turn pump on
        if (easy_input('Did the pump turn on?') == False): #verify real world
            pi.write(pins.getPin('PUMP'), 0) #set pump GPIO to low in case pump starts working again
            print("Error occured while turning the pump on\n")
            logging.error("Error, pump hardware seems to have failed") #log results
        else:
            pi.write(pins.getPin('PUMP'), 0) #turn fan two back off
            logging.debug("The pump turns on") #log results
    else:
        print("Unable to test pump due to potentially unsafe water level\n")
        logging.error("Error, unable to test pump due to potentially unsafe water level")
except Exception as e:
    print("Error occured while writing to pump pin\n")
    logging.error("Error, failed to write to pump pin: %s" % e)

print("Pump tests have been completed\n")

#Test the lights
print("Now testing the light\n")
try:
    pi.set_mode(pins.getPin('LIGHT'), pigpio.OUTPUT) #set light pin to OUTPUT
    pi.write(pins.getPin('LIGHT'), 0) #start with light off
    pi.write(pins.getPin('LIGHT'), 1) #turn light on
    time.sleep(5) #wait 5 seconds
    pi.write(pins.getPin('LIGHT'), 0) #turn light off

    if (easy_input('Did the light turn on for 5 seconds, then turn off?') == False):
        print("Error occured while turning the light on\n")
        logging.error("Error, failed to turn the light on: POSSIBLE HARDWARE ISSUE")
    else:
        print("Successfully cycled the light\n")
        logging.debug("Successfully cycled lights")
except Exception as e:
    print("Error occured while trying to write to the light\n")
    logging.error("Error occured while writing to the light: %s" % e)
print("Light tests have been completed\n")

print("All tests have been completed\n")
