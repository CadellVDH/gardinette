import board #oled tools
import adafruit_ssd1306 #oled screen
import digitalio #oled tools
import Adafruit_ADS1x15 #soil moisture sensor
import os #tools for working with the CLI
import logging #needed for logging
import pigpio #needed for GPIO control
from pigpio_dht import DHT22 #temp and humidity sensor
from configparser import ConfigParser #ini file manipulation
from datetime import datetime #needed for logging
from PIL import Image, ImageDraw, ImageFont #oled tools

#The purpose of this script is to ensure that all peripheral hardware
#components are connected and functioning properly, prior to startup
#as well as during troubleshooting

#Get current directory for log files and for pin file
PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
PATH = "%s/Pinout.ini" % PROJECT_DIRECTORY

#Look for pinout file and create one if it does not exist. Otherwise, write the file values to variables
Config = ConfigParser()
if (os.path.isfile(PATH) == False): #check if file already exists
    Pinout = open(PATH, "w+") #create file if none exists
    Pinout.close()
    Config.add_section('Pin_Values')
    Config.add_section('Address_Values')
    Config.set('Pin_Values', 'FAN_ONE', '13') #set value of FAN_ONE in ini file
    Config.set('Pin_Values', 'FAN_TWO', '12') #set value of FAN_TWO in ini file
    Config.set('Pin_Values', 'ADC_PIN', '1') #set value of ADC_PIN in ini file
    Config.set('Pin_Values', 'ADC_GAIN', '1') #set value of ADC_GAIN in ini file
    Config.set('Pin_Values', 'PUMP', '17') #set value of PUMP in ini file
    Config.set('Pin_Values', 'LIGHT', '27') #set value of LIGHT in ini file
    Config.set('Pin_Values', 'FLOAT', '22') #set value of FLOAT in ini file
    Config.set('Pin_Values', 'TEMP', '23') #set value of TEMP in ini file
    Config.set('Pin_Values', 'BUTTON_ONE', '6') #set value of BUTTON_ONE in ini file
    Config.set('Pin_Values', 'BUTTON_TWO', '16') #set value of BUTTON_TWO in ini file
    Config.set('Pin_Values', 'BUTTON_THREE', '26') #set value of BUTTON_THREE in ini file
    Config.set('Address_Values', 'OLED', '0x3c') #set value of OLED in ini file
    with open('Pinout.ini', 'w') as configfile: #open pinout.ini as file object
        Config.write(configfile) #save ini file

#set all needed pins based on config file
Config.read(PATH) #begin reading the config file
FAN_ONE = int(Config.get('Pin_Values', 'FAN_ONE')) #set FAN_ONE to value read in config file
FAN_TWO = int(Config.get('Pin_Values', 'FAN_TWO')) #set FAN_TWO to value read in config file
ADC_PIN = int(Config.get('Pin_Values', 'ADC_PIN')) #set ADC_PIN to value read in config file
ADC_GAIN = int(Config.get('Pin_Values', 'ADC_GAIN')) #set ADC_GAIN to value read in config file
PUMP = int(Config.get('Pin_Values', 'PUMP')) #set PUMP to value read in config file
LIGHT = int(Config.get('Pin_Values', 'LIGHT')) #set LIGHT to value read in config file
FLOAT = int(Config.get('Pin_Values', 'FLOAT')) #set FLOAT to value read in config file
TEMP = int(Config.get('Pin_Values', 'TEMP')) #set TEMP to value read in config file
BUTTON_ONE = int(Config.get('Pin_Values', 'BUTTON_ONE')) #set BUTTON_ONE to value read in config file
BUTTON_TWO =  int(Config.get('Pin_Values', 'BUTTON_TWO')) #set BUTTON_TWO to value read in config file
BUTTON_THREE = int(Config.get('Pin_Values', 'BUTTON_THREE')) #set BUTTON_THREE to value read in config file
OLED = Config.get('Address_Values', 'OLED') #set OLED address to value read in config file

#Open a log file to save diagnostic data
TODAY = datetime.now()
LOG_FILE = "%s/Logs/" % PROJECT_DIRECTORY + TODAY.strftime("%d-%m-%y-%H:%M") #name log file based on date and time
if (os.path.isdir("%s/Logs/" % PROJECT_DIRECTORY) == False):
    os.mkdir("%s/Logs/" % PROJECT_DIRECTORY)
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, filemode='w')

#Begin hardware diagnostics

#First test the OLED screen
print("Now testing the OLED screen...\n")
try: #attempt to detect the OLED
    print("Attempting to detect OLED...\n")
    oled_reset = digitalio.DigitalInOut(board.D4) #reset oled
    i2c = board.I2C() #these next few lines initialize the OLED
    oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c,reset=oled_reset) #specify oled we're using
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

user_test = input('Was the text "Gardinette!" shown? (Y/N)') #ask user to verify real world
while (user_test != "Y" and user_test != "N"): #ask user for input until they input the correct format
    print('Please enter only "Y" or "N"\n')
    user_test = input('Was the text "Gardinette!" shown? (Y/N)')
if (user_test == "N"):
    print("Error occured while writing to OLED screen\n")
    logging.error("Error, OLED hardware seems to have failed") #log results
else:
    print("OLED tests have succeeded\n")
    logging.debug("OLED hardware is operational") #log results

print("All OLED tests have been completed\n")

#Next test the ADC/moisture sensor
print("Now testing the ADC/Moisture Sensor\n")
adc = Adafruit_ADS1x15.ADS1115() #store ADC class to variable
print("Attempting to read value from ADC\n")
try:
    ADCvalue = adc.read_adc(ADC_PIN, gain=ADC_GAIN) #ATTEMPT TO READ ADC
    print("ADC value: %f\n" % ADCvalue) #print ADC value to console
    print("ADC succesffully read\n")
    logging.debug("ADC succesffully read") #log results
except Exception as e:
    print("Error occured while reading ADC value\n")
    logging.error("Error occured while reading ADC: %s" % e) #log results

print("All ADC tests have been completed\n")

#Test the temperature and humidity sensor
print("Now testing the temperature and humidity sensor\n")
DHT_SENSOR = DHT22(TEMP) #instantiate DHT sensor

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
    pi.set_mode(FAN_ONE, pigpio.OUTPUT) #set FAN_ONE to output

    pi.write(FAN_ONE, 1) #set FAN_ONE GPIO to high
    user_test = input('Did fan one turn on (Y/N)') #ask user to verify real world
    while (user_test != "Y" and user_test != "N"): #ask user for input until they input the correct format
        print('Please enter only "Y" or "N"\n')
        user_test = input('Did fan one turn on (Y/N)')
    if (user_test == "N"):
        print("Error occured while turning fan one on\n")
        logging.error("Error, fan hardware seems to have failed") #log results
    else:
        pi.write(FAN_ONE, 0) #turn fan one back off
        logging.debug("Fan one turns on") #log results
except Exception as e:
    print("Error occured while turning fan one on\n")
    logging.error("Error, failed to write to fan one GPIO: %s" % e)

try: #test if fan two turns on
    print("Checking if fan two turns on\n")
    pi.set_mode(FAN_TWO, pigpio.OUTPUT) #set FAN_TWO to output

    pi.write(FAN_TWO, 1) #set FAN_TWO GPIO to high
    user_test = input('Did fan two turn on (Y/N)') #ask user to verify real world
    while (user_test != "Y" and user_test != "N"): #ask user for input until they input the correct format
        print('Please enter only "Y" or "N"\n')
        user_test = input('Did fan two turn on (Y/N)')
    if (user_test == "N"):
        print("Error occured while turning fan two on\n")
        logging.error("Error, fan hardware seems to have failed") #log results
    else:
        pi.write(FAN_TWO, 0) #turn fan two back off
        logging.debug("Fan two turns on") #log results
except Exception as e:
    print("Error occured while turning fan two on\n")
    logging.error("Error, failed to write to fan two GPIO: %s" % e)

input("Please wait until both fans have stopped, then press [Enter]...")

try: #test if fan one works with PWM
    print("Checking if fan one speed control works\n")
    pi = pigpio.pi() #create instance of pigpio.pi class

    pi.set_PWM_dutycycle(FAN_ONE, 128) #set FAN_ONE GPIO 50% PWM
    user_test = input('Did fan one turn on (Y/N)') #ask user to verify real world
    while (user_test != "Y" and user_test != "N"): #ask user for input until they input the correct format
        print('Please enter only "Y" or "N"\n')
        user_test = input('Did fan one turn on (Y/N)')
    if (user_test == "N"):
        print("Error occured while turning fan one on\n")
        logging.error("Error, fan hardware seems to have failed") #log results
    else:
        pi.set_PWM_dutycycle(FAN_ONE, 0) #turn fan two back off
        logging.debug("Fan one turns on") #log results
except Exception as e:
    print("Error occured while turning fan one on\n")
    logging.error("Error, failed to write to fan one GPIO: %s" % e)

try: #test if fan two works with PWM
    print("checking if fan two speed control works\n")

    pi.set_PWM_dutycycle(FAN_TWO, 128) #set FAN_TWO GPIO 50% PWM
    user_test = input('Did fan two turn on (Y/N)') #ask user to verify real world
    while (user_test != "Y" and user_test != "N"): #ask user for input until they input the correct format
        print('Please enter only "Y" or "N"\n')
        user_test = input('Did fan two turn on (Y/N)')
    if (user_test == "N"):
        print("Error occured while turning fan two on\n")
        logging.error("Error, fan hardware seems to have failed") #log results
    else:
        pi.set_PWM_dutycycle(FAN_TWO, 0) #turn fan two back off
        logging.debug("Fan two turns on") #log results
except Exception as e:
    print("Error occured while turning fan two on\n")
    logging.error("Error, failed to write to fan two GPIO: %s" % e)

print("Fan tests have been completed\n")

#Test the pump
print("Now testing the pump\n")
try:
    pi.write(PUMP, 1 #turn pump on
    user_test = input('Did the pump turn on (Y/N)') #ask user to verify real world
    while (user_test != "Y" and user_test != "N"): #ask user for input until they input the correct format
        print('Please enter only "Y" or "N"\n')
        user_test = input('Did the pump turn on (Y/N)')
    if (user_test == "N"):
        print("Error occured while turning the pump on\n")
        logging.error("Error, pump hardware seems to have failed") #log results
    else:
        pi.write(PUMP, 0) #turn fan two back off
        logging.debug("The pump turns on") #log results
except Exception as e:
    print("Error occured while writing to pump pin\n")
    logging.error("Error, failed to write to pump pin: %s" % e)

print("Pump tests have been completed\n")

print("All tests have been completed\n")
