import board #oled tools
import adafruit_ssd1306 #oled screen
import digitalio #oled tools
import Adafruit_ADS1x15 #soil moisture sensor
import os #tools for working with the CLI
import logging #needed for logging
import pigpio #needed for GPIO control
import time #needed for function timing
import threading #needed for OLED data continuous updating
import csv #needed for temporary data logging
import config as global_vars #import global variable initialization module
from pigpio_dht import DHT22 #temp and humidity sensor
from datetime import datetime #needed for control timing
from PIL import Image, ImageDraw, ImageFont #oled tools
from CalibrationAndDiagnostics.helpers import * #import helper functions and classes

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

##Create a class for handling variable target values, including default target values
class target:
    'This class creates and accesses the Target.ini file'

    #Get current directory for target value file
    PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
    PATH = "%s/Data/Target.ini" % PROJECT_DIRECTORY

    ##Create an initialization function for creating a default pinout file
    def __init__(self):
        if (os.path.isfile(target.PATH) == False): #check if file already exists
            self.Target = open(target.PATH, "w+") #create file if none exists
            self.Target.close()

            self.configfile = open(target.PATH, "w+")
            self.Config = ConfigParser()

            self.Config.add_section('Water')
            self.Config.add_section('Soil')
            self.Config.add_section('Light')
            self.Config.add_section('Temp')
            self.Config.add_section('Humidity')

            self.Config.set('Light', 'Hours', '16') #set value of lighting hours in ini file
            self.Config.set('Light', 'Time', '12:00') #set value of lighting start time in ini file
            self.Config.set('Water', 'Water', '12:00') #set value of water start time in ini file
            self.Config.set('Soil', 'Soil', '25') #set value of soil moisture in ini file
            self.Config.set('Temp', 'Temp', '70') #set value of temperature in ini file
            self.Config.set('Humidity', 'Humidity', '55') #set value of humidity in ini file

            self.Config.write(self.configfile) #save ini file
            self.configfile.close()

    #Create a function for getting target values from the Target.ini file
    #param - parameter to be adjusted (Water, Soil, Hours, etc)
    #parent - config section to look in (Light, Water, Soil, etc)
    def getTarget(self, param, parent=None):
        self.Config = ConfigParser()
        self.Config.read(target.PATH)

        try:
            if parent == None:
                return self.Config.get(param, param) #return target based on Target.ini file
            else:
                return self.Config.get(parent, param) #return target based on Target.ini file
        except Exception as e:
            logging.error("Failed to get target value: %s" % e)
            return None

    #Create a function for setting values in the Target.ini file
    #param - parameter to be adjusted (Water, Soil, Hours, etc)
    #value - new target value to be added
    #parent - config section to look in (Light, Water, Soil, etc)
    def setTarget(self, param, value, parent=None):
        self.Config = ConfigParser()
        self.Config.read(target.PATH)
        self.configfile = open(target.PATH, "w+")

        try:
            if parent == None:
                self.Config.set(param, param, str(value)) #if param has no parent, param is the parent and also the section
            else:
                self.Config.set(parent, param, str(value)) #otherise, parent is the section
        except Exception as e:
            logging.error("Failed to set target value: %s" % e)
            return 'Failed'

        with open(target.PATH, 'w') as configfile: #open pinout.ini as file object
            self.Config.write(configfile) #save ini file

#Create a function which returns the current temp and humidity using sampling
def getTempHumidity(DHT_SENSOR, samples=5):

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
                i = i - 1 #subtract from i until there are 5 valid results
            i = i + 1

        #calculate the average for each
        temperature = int(sum(temp_list)/samples)
        humidity = int(sum(hum_list)/samples)
        print(temperature)
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

##Create a class which displays key data periodically
class dataGlance(threading.Thread):
    #Create a function to initialize threads and data variables
    def __init__(self):
        threading.Thread.__init__(self)
        self.pins = pinout() #initialize pinout
        self.oled = oled_utility(128, 32, self.pins.getAddr('OLED')) #initialize OLED display

    #Create a function to run the thread
    def run(self):
        #Create a loop to loop through data to display
        while global_vars.data_glance_exit_flag == False:
            self.oled.write_center(global_vars.current_temp, title="Temp") #write temp
            for i in range(0, 1000): #Create controlled delay which intermittently checks for exit flag
                if global_vars.data_glance_exit_flag == False:
                    i = i + 1
                    time.sleep(0.01)
                else:
                    break
            self.oled.write_center(global_vars.current_humidity, title="Humidity") #write humidity
            for i in range(0, 1000): #Create controlled delay which intermittently checks for exit flag
                if global_vars.data_glance_exit_flag == False:
                    i = i + 1
                    time.sleep(0.01)
                else:
                    break
            self.oled.write_center(global_vars.current_soil, title="Soil") #write soil
            for i in range(0, 1000): #Create controlled delay which intermittently checks for exit flag
                if global_vars.data_glance_exit_flag == False:
                    i = i + 1
                    time.sleep(0.01)
                else:
                    break

##Create a class which collects and stores data as fast as the sensors allow
class dataCollect(threading.Thread):
    #Create a function to initialize thread and data variables
    def __init__(self, TEMP, FLOAT):
        threading.Thread.__init__(self)
        self.FLOAT = FLOAT

        #Initialize DHT 22
        self.DHT_SENSOR = DHT22(TEMP)

        #initialize pigpio
        self.pi = pigpio.pi() #Initialize pigpio

        #Attempt to initialize sensor data
        try:
            [global_vars.current_temp, global_vars.current_humidity] = getTempHumidity(self.DHT_SENSOR)
            global_vars.current_soil = getSoilMoisture()
            global_vars.current_float = getFloat(self.pi, self.FLOAT)
        except Exception as e:
            logging.error("Failed one or more sensor readings: %s" % e) #exception block to prevent total failure if any sensor fails a reading

        #Reinitialize sensor with higher timeout
        self.DHT_SENSOR = DHT22(TEMP, timeout_secs=5)
    #Create a function to run the thread
    def run(self):
        #Create a loop to constantly check and update the sensor data values
        while True:
            #Get current sensor values
            try:
                [global_vars.current_temp, global_vars.current_humidity] = getTempHumidity(self.DHT_SENSOR)
                global_vars.current_soil = getSoilMoisture()
                global_vars.current_float = getFloat(self.pi, self.FLOAT)

            except Exception as e:
                logging.error("Failed one or more sensor readings: %s" % e) #exception block to prevent total failure if any sensor fails a reading

            time.sleep(5) #give the sensors a 5 second rest

##Create a class which runs a thread that periodically logs sensor data and actuation times
class dataLogger(threading.Thread):
    #Create a function to intialize the thread
    def __init__(self):
        threading.Thread.__init__(self)

    #Create a function to run the thread
    def run(self):
        #temporary code to make a csv of sensor data
        PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) #Get current directory for log files and for pin file
        path = "%s/Data/SensorData.csv" % PROJECT_DIRECTORY

        #Create the main loop to poll the sensor variables
        while True:
            pump = False
            light_initial = global_vars.currently_lighting
            light_final = light_initial
            interval = False #tracks whether it is within a 5 minute (5 or 0)
            events = [] #holds events that occured

            #Create a loop that polls for changes in pumping or lighting at 5 minute intervals
            while int(time.strftime("%M")) % 5 == 0:
                if global_vars.currently_pumping == True:
                    pump = True
                light_final = global_vars.currently_lighting
                interval = True

            #If minute is divisible by 5
            if interval == True:

                if pump == True:
                    events.append("Pumped")
                    pump = False

                if light_initial == False and light_final == True:
                    events.append("Light on")
                elif light_initial == True and light_final == False:
                    events.append("Light off")

                data_row = [datetime.now(), global_vars.current_temp, global_vars.current_humidity, global_vars.current_soil]
                data_row.extend(events)

                #temporary code to write to csv
                with open(path, mode='a') as data:
                    data_writer = csv.writer(data)
                    data_writer.writerow(data_row)

##Create a class which adjusts target parameters based on the OLED menu and stores the values
class targetAdjust(threading.Thread):
    #Create a function to initialize the thread and target object
    def __init__(self):
        threading.Thread.__init__(self)
        self.target = target() #create instance of target object

    #Create function to run the thread, which allows the user to adjust each parameter and stores it to the Target.ini file
    def run(self):
        [self.user_choice, self.node] = target_select()
        if self.user_choice != None: #if user selected a value
                  if self.node.parent.option == "Light": #If the parent is light, be sure to include it in the ini file update
                      self.target.setTarget(self.node.option, self.user_choice, parent="Light")
                  else: #otherwise include only the parameter and value
                    self.target.setTarget(self.node.option, self.user_choice)
        time.sleep(1) #sleep 1 second to prevent user from entering into target adjustment mode again

##Create a class for operating the pump
class pumpControl(threading.Thread):
    #Create a function to initalize the thread and target soil moisture value
    def __init__(self, PUMP):
        threading.Thread.__init__(self)
        self.target = target() #create instance of target object
        self.pi = pigpio.pi() #Initialize pigpio
        self.pump = PUMP

    #Create a function to run the thread, which monitors the time, soil level, and float sensor to control the pump
    def run(self):
        float_down = 0 #track how long float_sensor is down
        #Create inifinite loop for controlling the pump indefinitely
        while True:
            #Put entire loop in try block in case of multiple attempts at accessing Targets.ini file
            try:
                current_time = time.strftime("%H:%M") #store current time
                target_time = self.target.getTarget("Water") #store target time

                #if it's time to water, begin other necessary checks
                if current_time == target_time:
                    if global_vars.current_float != 0: #if float sensor if up, it's fine to water
                        float_down = 0 #reset count of times float has been down
                        target_soil = self.target.getTarget("Soil") #get target soil moisture value

                        #run the pump until the timer hits 30 seconds or the current soil moisture is greater than the target
                        t = 0 #reset timer
                        while t <= 90 and global_vars.current_soil<int(target_soil):
                            global_vars.currently_pumping = True
                            self.pi.write(self.pump, 1) #run pump
                            t = t + 1 #increase timer
                            time.sleep(1) #1 second delay
                        global_vars.currently_pumping = False
                        self.pi.write(self.pump, 0) #turn pump back off
                        time.sleep(30)
                    elif global_vars.current_float == 0 and float_down < 4: #continue pumping as long as pump counter is less than 4 (4 days)
                        float_down = float_down + 1 #increment counter for each watering
                        target_soil = self.target.getTarget("Soil") #get target soil moisture value

                        #run the pump until the timer hits 30 seconds or the current soil moisture is greater than the target
                        t = 0 #reset timer
                        while t <= 90 and global_vars.current_soil<int(target_soil):
                            global_vars.currently_pumping = True
                            self.pi.write(self.pump, 1) #run pump
                            t = t + 1 #increase timer
                            time.sleep(1) #1 second delay
                        global_vars.currently_pumping = False
                        self.pi.write(self.pump, 0) #turn pump back off
                        time.sleep(30)
            except Exception as e:
                logging.error("Failed to control pump: %s" % e)

##Create a class for operating the light
class lightControl(threading.Thread):
    #Create a function to initialize the thread and target "on" time and hours of light
    def __init__(self, LIGHT):
        threading.Thread.__init__(self)
        self.target = target() #create instance of target object
        self.pi = pigpio.pi() #initialize pigpio
        self.light = LIGHT

    #Create a funcion to calculate end time based on start time and hours
    def endTime(self, start, hours):
        minutes = int(60 * int(hours)) #calculate number of minutes in case of decimal hours
        remaining_minutes = minutes % 60 #calculate number of non-whole hour minutes
        whole_hours = (minutes-remaining_minutes) / 60 #calculate number of whole number hours

        start_hour = int(start[0:2]) #extract starting hour
        start_minute = int(start[3:5]) #extract starting minute

        #first add the number of hours and minutes
        end_hour = int(start_hour + whole_hours)
        end_minute = int(start_minute + remaining_minutes)

        #check if hours are over 23 or minutes are over 59 then subtract 24 and 60 respectively
        if end_hour > 23:
            end_hour = end_hour - 24
        if end_minute > 59:
            end_minute = end_minute - 60

        #format the string appropriately
        if end_hour < 10:
            end_hour = "0%s" % end_hour #add 0 to beginning if < 10
        if end_minute < 10:
            end_minute = "0%s" % end_minute #add 0 to beginning if < 10

        return "{}:{}".format(end_hour, end_minute) #return formatted string

    #Create a function which operates the light based on the time of day
    def run(self):
        #Create an indefinite loop to monitor the time of day and target hours of light to control the light
        while True:
            #Place whole thing in try block in case Target.ini is being modified while endTime is running
            try:
                current_time = time.strftime("%H:%M") #store current time
                target_time = self.target.getTarget("Time", parent="Light") #store target time
                target_hours = self.target.getTarget("Hours", parent="Light") #store number of hours to run

                end_time = self.endTime(target_time, target_hours) #calculate end time

                #turn light on if it passes checks necessary to be within time range
                if current_time >= target_time and current_time < end_time:
                    self.pi.write(self.light, 1) #turn light on
                    global_vars.currently_lighting = True
                elif current_time >= target_time and end_time<target_time:
                    self.pi.write(self.light, 1) #turn light on
                    global_vars.currently_lighting = True
                elif current_time<end_time and end_time<target_time:
                    self.pi.write(self.light, 1) #turn light on
                    global_vars.currently_lighting = True
                elif target_time == end_time:
                    self.pi.write(self.light, 1) #turn light on
                    global_vars.currently_lighting = True
                else:
                    self.pi.write(self.light, 0) #turn light off otherwise
                    global_vars.currently_lighting = False
            except Exception as e:
                    logging.error("Failed to control light, reattempting: %s" % e)

##Create a class for operating the fans
class fanControl(threading.Thread):
    #Create a function to initalize the thread and the target and pigpio instances
    def __init__(self, FAN_ONE, FAN_TWO):
        threading.Thread.__init__(self)
        self.target = target() #create instance of target object
        self.pi = pigpio.pi() #initialize pigpio
        self.fan_one = FAN_ONE
        self.fan_two = FAN_TWO

    #Create a function to run the thread
    def run(self):
        while True:
            try:
                target_humidity = int(self.target.getTarget("Humidity")) #get current target humidity
                target_temp = int(self.target.getTarget("Temp")) #get current target temp

                #If either temp or humidity is too high, turn the fans on (or if temp = 0, then turn fans on to be safe)
                if global_vars.current_temp>target_temp or global_vars.current_humidity>target_humidity or global_vars.current_temp == 0:
                    self.pi.write(self.fan_one, 1)
                    self.pi.write(self.fan_two, 1)
                else: #otherwise make sure theyr're off
                    self.pi.write(self.fan_one, 0)
                    self.pi.write(self.fan_two, 0)
            except Exception as e:
                logging.error("Failed to control temp or humidity: %s" % e)

##Create a class responsible for all aspects of actuator control
class actuatorControl(threading.Thread):
    #Create a function to initalize the thread and all necessary object instances
    def __init__(self,PUMP, LIGHT, FAN_ONE, FAN_TWO):
        threading.Thread.__init__(self)
        self.target = target() #create instance of target object
        self.pi = pigpio.pi() #initialize pigpio

        #intialize all pin number variables
        self.pump = PUMP
        self.light = LIGHT
        self.fan_one = FAN_ONE
        self.fan_two = FAN_TWO

    #Create a funcion to calculate end time based on start time and hours
    def endTime(self, start, hours):
        minutes = int(60 * int(hours)) #calculate number of minutes in case of decimal hours
        remaining_minutes = minutes % 60 #calculate number of non-whole hour minutes
        whole_hours = (minutes-remaining_minutes) / 60 #calculate number of whole number hours

        start_hour = int(start[0:2]) #extract starting hour
        start_minute = int(start[3:5]) #extract starting minute

        #first add the number of hours and minutes
        end_hour = int(start_hour + whole_hours)
        end_minute = int(start_minute + remaining_minutes)

        #check if hours are over 23 or minutes are over 59 then subtract 24 and 60 respectively
        if end_hour > 23:
            end_hour = end_hour - 24
        if end_minute > 59:
            end_minute = end_minute - 60

        #format the string appropriately
        if end_hour < 10:
            end_hour = "0%s" % end_hour #add 0 to beginning if < 10
        if end_minute < 10:
            end_minute = "0%s" % end_minute #add 0 to beginning if < 10

        return "{}:{}".format(end_hour, end_minute) #return formatted string

    #Create a function to run the thread
    def run(self):
        float_down = 0 #track how long float_sensor is down
        #Create inifinite loop for controlling the pump indefinitely
        while True:
            #LIGHT CONTROL
            try:
                current_time = time.strftime("%H:%M") #store current time
                target_time = self.target.getTarget("Time", parent="Light") #store target time
                target_hours = self.target.getTarget("Hours", parent="Light") #store number of hours to run

                end_time = self.endTime(target_time, target_hours) #calculate end time

                #turn light on if it passes checks necessary to be within time range
                if current_time >= target_time and current_time < end_time:
                    self.pi.write(self.light, 1) #turn light on
                    global_vars.currently_lighting = True
                elif current_time >= target_time and end_time<target_time:
                    self.pi.write(self.light, 1) #turn light on
                    global_vars.currently_lighting = True
                elif current_time<end_time and end_time<target_time:
                    self.pi.write(self.light, 1) #turn light on
                    global_vars.currently_lighting = True
                elif target_time == end_time:
                    self.pi.write(self.light, 1) #turn light on
                    global_vars.currently_lighting = True
                else:
                    self.pi.write(self.light, 0) #turn light off otherwise
                    global_vars.currently_lighting = False
            except Exception as e:
                    logging.error("Failed to control light, reattempting: %s" % e)
            #PUMP CONTROL
            try:
                current_time = time.strftime("%H:%M") #store current time
                target_time = self.target.getTarget("Water") #store target time

                #if it's time to water, begin other necessary checks
                if current_time == target_time:
                    if global_vars.current_float != 0: #if float sensor if up, it's fine to water
                        float_down = 0 #reset count of times float has been down
                        target_soil = self.target.getTarget("Soil") #get target soil moisture value

                        #run the pump until the timer hits 30 seconds or the current soil moisture is greater than the target
                        t = 0 #reset timer
                        while t <= 90 and global_vars.current_soil<int(target_soil):
                            global_vars.currently_pumping = True
                            self.pi.write(self.pump, 1) #run pump
                            t = t + 1 #increase timer
                            time.sleep(1) #1 second delay
                        global_vars.currently_pumping = False
                        self.pi.write(self.pump, 0) #turn pump back off
                        time.sleep(30)
                    elif global_vars.current_float == 0 and float_down < 4: #continue pumping as long as pump counter is less than 4 (4 days)
                        float_down = float_down + 1 #increment counter for each watering
                        target_soil = self.target.getTarget("Soil") #get target soil moisture value

                        #run the pump until the timer hits 30 seconds or the current soil moisture is greater than the target
                        t = 0 #reset timer
                        while t <= 90 and global_vars.current_soil<int(target_soil):
                            global_vars.currently_pumping = True
                            self.pi.write(self.pump, 1) #run pump
                            t = t + 1 #increase timer
                            time.sleep(1) #1 second delay
                        global_vars.currently_pumping = False
                        self.pi.write(self.pump, 0) #turn pump back off
                        time.sleep(30)
            except Exception as e:
                logging.error("Failed to control pump: %s" % e)

            #FAN CONTROL
            try:
                target_humidity = int(self.target.getTarget("Humidity")) #get current target humidity
                target_temp = int(self.target.getTarget("Temp")) #get current target temp

                #If either temp or humidity is too high, turn the fans on (or if temp = 0, then turn fans on to be safe)
                if global_vars.current_temp>target_temp or global_vars.current_humidity>target_humidity or global_vars.current_temp == 0:
                    self.pi.write(self.fan_one, 1)
                    self.pi.write(self.fan_two, 1)
                else: #otherwise make sure theyr're off
                    self.pi.write(self.fan_one, 0)
                    self.pi.write(self.fan_two, 0)
            except Exception as e:
                logging.error("Failed to control temp or humidity: %s" % e)
