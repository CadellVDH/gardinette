import Adafruit_ADS1x15 #soil moisture sensor
import os #tools for working with the CLI
from configparser import ConfigParser #ini file manipulation
from statistics import mean #math

##Create a function for reading the ADC
def adc_read(retry=1):
    Config = ConfigParser()
    PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
    PATH = "%s/Pinout.ini" % PROJECT_DIRECTORY
    Config.read(PATH) #begin reading the config file
    adc = Adafruit_ADS1x15.ADS1115() #store ADC class to variable
    pins = pinout() #create instance of pinout class
    readings = []
    for i in range(0, retry):
        readings.append(adc.read_adc(pins.ADC_PIN, gain=pins.ADC_GAIN))
    return int(mean(readings))

class pinout():
    'This class creates and accesses the pinout.ini file'

    ##Create an initialization function for creating a default pinout file
    def __init__():
        #Get current directory for pin file
        PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
        PATH = "%s/Pinout.ini" % PROJECT_DIRECTORY
        Config = ConfigParser()
        if (os.path.isfile(PATH) == False): #check if file already exists
            Pinout = open(PATH, "w+") #create file if none exists
            Pinout.close()
            Config.add_section('Pin_Values')
            Config.add_section('Address_Values')
            Config.add_section('Calibration_Constants')
            Config.set('Pin_Values', 'FAN_ONE', '13') #set value of FAN_ONE in ini file
            Config.set('Pin_Values', 'FAN_TWO', '12') #set value of FAN_TWO in ini file
            Config.set('Pin_Values', 'ADC_PIN', '1') #set value of ADC_PIN in ini file
            Config.set('Pin_Values', 'ADC_GAIN', '1') #set value of ADC_GAIN in ini file
            Config.set('Pin_Values', 'PUMP', '17') #set value of PUMP in ini file
            Config.set('Pin_Values', 'LIGHT', '27') #set value of LIGHT in ini file
            Config.set('Pin_Values', 'FLOAT', '4') #set value of FLOAT in ini file
            Config.set('Pin_Values', 'TEMP', '23') #set value of TEMP in ini file
            Config.set('Pin_Values', 'BUTTON_ONE', '6') #set value of BUTTON_ONE in ini file
            Config.set('Pin_Values', 'BUTTON_TWO', '16') #set value of BUTTON_TWO in ini file
            Config.set('Pin_Values', 'BUTTON_THREE', '26') #set value of BUTTON_THREE in ini file
            Config.set('Address_Values', 'OLED', 0x3c) #set value of OLED in ini file
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
    OLED = int(Config.get('Address_Values', 'OLED'), 0) #set OLED address to value read in config file, base 0

##Create a function for writing to config files
def config_write(section, name, value):
    #Get current directory for pin file
    PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
    PATH = "%s/Pinout.ini" % PROJECT_DIRECTORY
    Config = ConfigParser()
    Config.read(PATH) #read pinout file (for current section names)
    Config.set(section, name, str(value)) #set value of name in section
    with open(PATH, 'w') as configfile: #open pinout.ini as file object
        Config.write(configfile) #save ini file

##Create a function for taking and scrubbing user input for yes/no questions
def easy_input(prompt):
    user_test = input('%s (Y/N)' % prompt) #append yes/no to end of question
    while (user_test.lower() != "y" and user_test.lower() != "n"): #disregard case of entered input
        user_test = input('Please enter only "Y" or "N"\n%s (Y/N)', prompt) #repeat until they answer

    if (user_test.lower() == "y"):
        return_value = True
    else:
        return_value = False

    return return_value
