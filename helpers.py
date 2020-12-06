import Adafruit_ADS1x15 #soil moisture sensor
import os #tools for working with the CLI
import board #oled tools
import adafruit_ssd1306 #oled screen
import digitalio #oled tools
from configparser import ConfigParser #ini file manipulation
from statistics import mean #math
from PIL import Image, ImageDraw, ImageFont #oled tools

##Create a class for handling variable pinouts that may change depending on the chosen carrier board
class pinout():
    'This class creates and accesses the pinout.ini file'

    #Get current directory for pin file
    PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
    PATH = "%s/Pinout.ini" % PROJECT_DIRECTORY

    ##Create an initialization function for creating a default pinout file
    def __init__(self):
        if (os.path.isfile(pinout.PATH) == False): #check if file already exists
            Pinout = open(pinout.PATH, "w+") #create file if none exists
            Pinout.close()
            Config = ConfigParser()
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

    #Create a function for getting pins from pinout.ini file
    def getPin(self, pin):
        Config = ConfigParser()
        Config.read(pinout.PATH)
        try:
            return int(Config.get('Pin_Values', pin)) #return pin based on pinout.ini file
        except:
            return None

    #Create a function for getting address values from pinout.ini file
    def getAddr(self, device):
        Config = ConfigParser()
        Config.read(pinout.PATH)
        try:
            return int(Config.get('Address_Values', device), 0) #return base 0 address value
        except:
            return None

##Create class for initializing and interacting with the OLED display
class oled_utility():
    'This class initializes and writes to the OLED display'

    ##Create a function to intialize dependencies
    def __init__(self, width, height, address):
        self.PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
        self.width = width #specify width and height for instnace
        self.height = height

        self.address = address #specify i2c address used

        self.i2c = board.I2C() #create i2c instance

        self.oled = adafruit_ssd1306.SSD1306_I2C(self.width, self.height, self.i2c, addr=self.address) #specify oled we're using

        self.oled.fill(0) #set screen to black
        self.oled.show() #send setting to screen

    ##Create a function for writing to the OLED display
    def write(self, message, x_pos, y_pos, font_size):
        self.image = Image.new("1", (self.oled.width, self.oled.height)) #create blank image
        self.draw = ImageDraw.Draw(self.image) #draw blank Image

        self.font = ImageFont.truetype("%s/Hack-Regular.ttf" % self.PROJECT_DIRECTORY, font_size) #get text font
        self.draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=255, fill=0)

        self.draw.text((x_pos, y_pos), message, font=self.font, fill=255) #draw message at position

        self.oled.image(self.image) #create image
        self.oled.show() #draw image

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
        readings.append(adc.read_adc(pins.getPin('ADC_PIN'), gain=pins.getPin('ADC_GAIN')))
    return int(mean(readings))

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
