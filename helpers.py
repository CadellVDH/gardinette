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
    ADC_PIN = int(Config.get('Pin_Values', 'ADC_PIN')) #set ADC_PIN to value read in config file
    ADC_GAIN = int(Config.get('Pin_Values', 'ADC_GAIN')) #set ADC_GAIN to value read in config file
    adc = Adafruit_ADS1x15.ADS1115() #store ADC class to variable
    readings = []
    for i in range(0, retry):
        readings.append(adc.read_adc(ADC_PIN, gain=ADC_GAIN))
    return int(mean(readings))

##Create a function for creating a default pinout file
def pinout_init():
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
        Config.set('Address_Values', 'OLED', '0x3c') #set value of OLED in ini file
        with open('Pinout.ini', 'w') as configfile: #open pinout.ini as file object
            Config.write(configfile) #save ini file

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
