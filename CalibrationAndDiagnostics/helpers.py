import Adafruit_ADS1x15 #soil moisture sensor
import os #tools for working with the CLI
import board #oled tools
import adafruit_ssd1306 #oled screen
import digitalio #oled tools
import time #adding delays
import logging #needed for logging
from configparser import ConfigParser #ini file manipulation
from statistics import mean #math
from PIL import Image, ImageDraw, ImageFont #oled tools

##Create a class for handling variable pinouts that may change depending on the chosen carrier board
class pinout:
    'This class creates and accesses the pinout.ini file'

    #Get current directory for pin file
    PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
    PATH = "%s/Pinout.ini" % PROJECT_DIRECTORY

    ##Create an initialization function for creating a default pinout file
    def __init__(self):
        if (os.path.isfile(pinout.PATH) == False): #check if file already exists
            self.Pinout = open(pinout.PATH, "w+") #create file if none exists
            self.Pinout.close()

            self.configfile = open(pinout.PATH, "w+")
            self.Config = ConfigParser()

            self.Config.add_section('Pin_Values')
            self.Config.add_section('Address_Values')
            self.Config.add_section('Calibration_Constants')

            self.Config.set('Pin_Values', 'FAN_ONE', '13') #set value of FAN_ONE in ini file
            self.Config.set('Pin_Values', 'FAN_TWO', '12') #set value of FAN_TWO in ini file
            self.Config.set('Pin_Values', 'ADC_PIN', '1') #set value of ADC_PIN in ini file
            self.Config.set('Pin_Values', 'ADC_GAIN', '1') #set value of ADC_GAIN in ini file
            self.Config.set('Pin_Values', 'PUMP', '17') #set value of PUMP in ini file
            self.Config.set('Pin_Values', 'LIGHT', '27') #set value of LIGHT in ini file
            self.Config.set('Pin_Values', 'FLOAT', '4') #set value of FLOAT in ini file
            self.Config.set('Pin_Values', 'TEMP', '23') #set value of TEMP in ini file
            self.Config.set('Pin_Values', 'BUTTON_ONE', '26') #set value of BUTTON_ONE in ini file
            self.Config.set('Pin_Values', 'BUTTON_TWO', '16') #set value of BUTTON_TWO in ini file
            self.Config.set('Pin_Values', 'BUTTON_THREE', '6') #set value of BUTTON_THREE in ini file
            self.Config.set('Address_Values', 'OLED', '0x3c') #set value of OLED in ini file

            self.Config.write(self.configfile) #save ini file
            self.configfile.close()

    #Create a function for getting pins from pinout.ini file
    def getPin(self, pin):
        self.Config = ConfigParser()
        self.Config.read(pinout.PATH)
        try:
            return int(self.Config.get('Pin_Values', pin)) #return pin based on pinout.ini file
        except Exception as e:
            logging.error("Failed get pin: %s" % e)
            return None

    #Create a function for getting address values from pinout.ini file
    def getAddr(self, device):
        self.Config = ConfigParser()
        self.Config.read(pinout.PATH)
        try:
            return int(self.Config.get('Address_Values', device), 0) #return base 0 address value
        except Exception as e:
            logging.error("Failed get address: %s" % e)
            return None

##Create class for initializing and interacting with the OLED display
class oled_utility:
    'This class initializes and writes to the OLED display'

    ##Create a function to intialize dependencies
    def __init__(self, width, height, address):
        self.PROJECT_DIRECTORY = os.path.dirname(os.path.dirname(__file__))
        self.width = width #specify width and height for instnace
        self.height = height

        self.address = address #specify i2c address used

        self.i2c = board.I2C() #create i2c instance

        self.oled = adafruit_ssd1306.SSD1306_I2C(self.width, self.height, self.i2c, addr=self.address) #specify oled we're using

        self.oled.fill(0) #set screen to black
        self.oled.show() #send setting to screen

    ##Create a function for writing messages with titles, centered on the OLED
    def write_center(self, message, font_size=10, title=""):
        self.image = Image.new("1", (self.oled.width, self.oled.height)) #create blank image
        self.draw = ImageDraw.Draw(self.image) #draw blank Image

        self.font = ImageFont.truetype("%s/fonts/Hack-Regular.ttf" % self.PROJECT_DIRECTORY, 7) #get text font

        (self.font_width, self.font_height) = self.font.getsize(title) #get font width and height
        self.x_pos = self.width // 2 - self.font_width // 2 #move text to center
        self.draw.text((self.x_pos, 0), title, font=self.font, fill=255) #draw message at position

        self.font = ImageFont.truetype("%s/fonts/Hack-Regular.ttf" % self.PROJECT_DIRECTORY, font_size) #set to regular font size

        (self.font_width, self.font_height) = self.font.getsize(str(message)) #get font width and height
        self.x_pos = self.width // 2 - self.font_width // 2 #move text to center
        self.y_pos = self.height // 2 - self.font_height // 2 #move text to center
        self.draw.text((self.x_pos, self.y_pos), str(message), font=self.font, fill=255) #draw message at position

        self.oled.image(self.image) #create image
        self.oled.show() #draw image

    ##Create a function for writing messsages at a postion on the screen
    def write(self, message, x_pos, y_pos, font_size=10, clear=True):

        if (clear == True):
            self.image = Image.new("1", (self.oled.width, self.oled.height)) #create blank image
            self.draw = ImageDraw.Draw(self.image) #draw blank Image

        self.font = ImageFont.truetype("%s/fonts/Hack-Regular.ttf" % self.PROJECT_DIRECTORY, font_size) #set to regular font size

        self.x_pos = x_pos #set desired x and y position
        self.y_pos = y_pos

        self.draw.text((self.x_pos, self.y_pos), str(message), font=self.font, fill=255) #draw message at position

        self.oled.image(self.image) #create image
        self.oled.show() #draw image

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

#Create a function for choosing between menu options on the OLED
def menu():

    current_option = root #Set initial option to the root option
    position = 0 #set left/right position
    timer = 0 #start timer

    pins = pinout() #initialize pinout
    oled = oled_utility(128, 32, pins.getAddr('OLED')) #initialize OLED display
    pi = pigpio.pi() #Initialize pigpio
    BUTTON_ONE = pins.getPin('BUTTON_ONE')
    BUTTON_TWO = pins.getPin('BUTTON_TWO')
    BUTTON_THREE = pins.getPin('BUTTON_THREE')

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
                return current_option #and it's node is returned
        elif pi.read(BUTTON_THREE) == True:
            if position < len(current_option.children)-1: #if position is not at the end of the list
                position += 1 #move one spot to the right
            else:
                position = 0 #move position back to other end
            timer = 0 #reset timer
        else:
            timer += 1 #count the timer up

        time.sleep(.25) #1/4 second delay

    return None

#Create a function for choosing paramater values on the OLED
def param_adjust(choice_list, unit=""):
    timer = 0 #create a timer
    position = 0 #start at position 0

    pins = pinout() #initialize pinout
    oled = oled_utility(128, 32, pins.getAddr('OLED')) #initialize OLED display
    pi = pigpio.pi() #Initialize pigpio
    BUTTON_ONE = pins.getPin('BUTTON_ONE')
    BUTTON_TWO = pins.getPin('BUTTON_TWO')
    BUTTON_THREE = pins.getPin('BUTTON_THREE')

    while timer <= 400: #while elapsed time is less than 20 seonds
        oled.write_center(str(choice_list[position])) #print the current choice to the OLED
        oled.write(unit, oled.width/2+12, 10, clear=False) #write the unit above the number
        oled.write("<--", 0, oled.height/2, clear=False) #create left arrow
        oled.write("-->", oled.width-18, oled.height/2, clear=False) #create right arrow

        if pi.read(BUTTON_ONE):
            if position != 0:
                position -= 1 #move left
            else:
                position = len(choice_list) - 1 #otherwise go to end of choice_list

            timer = 0 #reset timer
        elif pi.read(BUTTON_TWO):
            return choice_list[position] #return the chosen value
        elif pi.read(BUTTON_THREE):
            if position < len(choice_list)-1: #if position is not at end of list
                position += 1 #move right
            else:
                position = 0 #move back to beginning
        else:
            timer += 1 #count the timer up

        time.sleep(.05) #1/10 second delay

    return None

#Create a function for the user to adjust box target values
def target_select():
    menu_choice = menu() #call the menu function to find out what parameter the user wants to adjust
    time.sleep(0.5) #delay so user doesn't accidentally choose first value

    if menu_choice == None:
        return None, None
    elif menu_choice.option == "Hours":
        allowed = list(range(1, 24)) #list is 1-24
        return param_adjust(allowed, "Hours"), menu_choice #return the target value and menu node
    elif menu_choice.option == "Time":
        allowed = [] #empty list
        for i in range(0, 24): #generate list
            for j in range(0, 56, 5):
                if j < 10 and i < 10:
                    allowed.append("0{}:0{}".format(i,j)) #make list with 0 in front of hour and minute if both less than 10
                elif j < 10:
                    allowed.append("{}:0{}".format(i,j)) #make list with 0 in front of minute if less than 10
                elif i < 10:
                    allowed.append("0{}:{}".format(i,j)) #make list with 0 in front of hour if less than 10
                else:
                    allowed.append("{}:{}".format(i,j)) #otherwise make list using only the minute
        return param_adjust(allowed), menu_choice #return the target value and menu node
    elif menu_choice.option == "Water":
        allowed = [] #empty list
        for i in range(0, 24): #generate list
            for j in range(0, 56, 5):
                if j < 10 and i < 10:
                    allowed.append("0{}:0{}".format(i,j)) #make list with 0 in front of hour and minute if both less than 10
                elif j < 10:
                    allowed.append("{}:0{}".format(i,j)) #make list with 0 in front of minute if less than 10
                elif i < 10:
                    allowed.append("0{}:{}".format(i,j)) #make list with 0 in front of hour if less than 10
                else:
                    allowed.append("{}:{}".format(i,j)) #otherwise make list using only the minute
        return param_adjust(allowed), menu_choice #return the target value and menu node
    elif menu_choice.option ==  "Soil":
        allowed = list(range(20, 80)) #create list of allowed soil moistures
        return param_adjust(allowed, "%"), menu_choice #return the target value and menu node
    elif menu_choice.option == "Temp":
        allowed = list(range(60, 90)) #create list of allowed temps
        return param_adjust(allowed, "F"), menu_choice #return the target value and menu node
    elif menu_choice.option == "Humidity":
        allowed = list(range(10, 90)) #create list of allowed humidities
        return param_adjust(allowed, "%"), menu_choice #return the target value and menu node
    else:
        return None, None

#Create a function which returns the current temp and humidity using sampling
def getTempHumidity(DHT_SENSOR, samples=2):

    try:
        #initialize temp and humidity lists
        temp_list = []
        hum_list = []

        i=0
        while i < samples:
            result = DHT_SENSOR.read() #attempt to read temp and humidity sensor

            #Check that values are reasonable
            if int(result["temp_f"]) < 175 and int(result["temp_f"]) > -40 and int(result["humidity"]) > 0 and int(result["humidity"]) < 100:
                temp_list.append(int(result["temp_f"])) #get temp separately in F
                hum_list.append(int(result["humidity"])) #get humidity separately
            else:
                i = i - 1 #subtract from i until there are "samples" valid results
            i = i + 1

        #calculate the average for each
        temperature = int(sum(temp_list)/samples)
        humidity = int(sum(hum_list)/samples)

        return temperature, humidity
    except Exception as e:
        logging.error("Error, Temp and humidity sensor failed to read: %s" % e)
        return global_vars.current_temp, global_vars.current_humidity #if reading fails return current values to prevent failure

#Create a function which returns the current soil mositure content
def getSoilMoisture():
    Config = ConfigParser() #initialize config parser and file path to get calibration curve
    Config.read(pinout.PATH)

    try:
        slope = int(float(Config.get('Calibration_Constants', 'slope'))) #return slope based on pinout.ini file
        intercept = int(float(Config.get('Calibration_Constants', 'intercept'))) #return intercept based on pinout.ini file
        soil_moisture = int((adc_read(retry=3)-intercept)/slope) #calculate soil mositure and convert to integer

        if soil_moisture <= 20:
            soil_moisture = 20 #soil mositure can't be less than 20% due to sensor limitations
        elif soil_moisture >= 80:
            soil_moisture = 80 #soil moisture can't be greater than 80% due to sensor limitations

        return soil_moisture
    except Exception as e:
        logging.error("Failed get soil mositure: %s" % e)
        return None #if reading fails return None to indicate failure

#Create a function which returns the float sensor value
def getFloat(pi, FLOAT):
    try:
        return pi.read(FLOAT)
    except Exception as e:
        logging.error("Failed to get float sensor value: %s" % e)
        return None #if reading fails return None to indicate failure

##Create a function for reading the ADC
def adc_read(retry=1):
    adc = Adafruit_ADS1x15.ADS1115() #store ADC class to variable
    pins = pinout() #create instance of pinout class
    readings = []
    for i in range(0, retry):
        readings.append(adc.read_adc(pins.getPin('ADC_PIN'), gain=pins.getPin('ADC_GAIN')))
        time.sleep(3)
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
        user_test = input('Please enter only "Y" or "N"\n%s (Y/N)' % prompt) #repeat until they answer

    if (user_test.lower() == "y"):
        return_value = True
    else:
        return_value = False

    return return_value
