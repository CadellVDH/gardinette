import Adafruit_ADS1x15 #soil moisture sensor
import os #tools for working with the CLI
from configparser import ConfigParser #ini file manipulation
from statistics import mean #math

##Create a function for reading the ADC
def adc_read(retry=1):
    Config = ConfigParser()
    PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
    path = "%s/Pinout.ini" % PROJECT_DIRECTORY
    Config.read(path) #begin reading the config file
    ADC_PIN = int(Config.get('Pin_Values', 'ADC_PIN')) #set ADC_PIN to value read in config file
    ADC_GAIN = int(Config.get('Pin_Values', 'ADC_GAIN')) #set ADC_GAIN to value read in config file
    adc = Adafruit_ADS1x15.ADS1115() #store ADC class to variable
    readings = []
    for i in range(0, retry):
        readings.append(adc.read_adc(ADC_PIN, gain=ADC_GAIN))
    return int(mean(readings))
