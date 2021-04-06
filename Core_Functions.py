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
        timer = 0 #create a timer for logging
        prev_light = global_vars.currently_lighting #store initial value of light

        #temporary code to make a csv of sensor data
        PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) #Get current directory for log files and for pin file
        path = "%s/Data/SensorData.csv" % PROJECT_DIRECTORY
        prev_log_time = int(time.strftime("%M")) #store the minute that data is logged

        #Create a loop to constantly check and update the sensor data values
        while True:
            #Get current sensor values
            try:
                [global_vars.current_temp, global_vars.current_humidity] = getTempHumidity(self.DHT_SENSOR)
                global_vars.current_soil = getSoilMoisture()
                global_vars.current_float = getFloat(self.pi, self.FLOAT)

            except Exception as e:
                logging.error("Failed one or more sensor readings: %s" % e) #exception block to prevent total failure if any sensor fails a reading

            #Check if it has been 5 minutes since last log
            if int(time.strftime("%M")) >= prev_log_time + 5 or (prev_log_time >= 56 and int(time.strftime("%M")) >= 5-(60-prev_log_time) and int(time.strftime("%M")) < 10):
                prev_log_time = int(time.strftime("%M")) #reset log time
                events = [] #create empty list of events

                #check if pump occured, then reset pump flag if it did
                if global_vars.pumped == True:
                    events.append("Pumped") #add "pumped" to events list
                    global_vars.pumped = False #reset pump flag

                #check if lighting status changed
                if global_vars.currently_lighting != prev_light:
                    #determine whether lights were turned on or off based on initial state
                    if prev_light == True:
                        events.append("Light Off")
                    else:
                        events.append("Light On")
                    prev_light = global_vars.currently_lighting #set previous lighting to the current value

                data_row = [datetime.now(), global_vars.current_temp, global_vars.current_humidity, global_vars.current_soil]
                data_row.extend(events)

                #temporary code to write to csv
                with open(path, mode='a') as data:
                    data_writer = csv.writer(data)
                    data_writer.writerow(data_row)

            time.sleep(5) #give the sensors a 5 second rest

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

##Create a class responsible for all aspects of actuator control
class actuatorControl(threading.Thread):
    #Create a function to initalize the thread and all necessary object instances
    def __init__(self, pi, PUMP, LIGHT, FAN_ONE, FAN_TWO):
        threading.Thread.__init__(self)
        self.target = target() #create instance of target object
        self.pi = pi

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
            time.sleep(10)
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
                        while t <= 40 and global_vars.current_soil<int(target_soil):
                            global_vars.pumped = True #set pumped flag to true to indicate the pump occured
                            self.pi.write(self.pump, 1) #run pump
                            t = t + 1 #increase timer
                            time.sleep(1) #1 second delay
                        self.pi.write(self.pump, 0) #turn pump back off

                    elif global_vars.current_float == 0 and float_down < 4: #continue pumping as long as pump counter is less than 4 (4 days)
                        float_down = float_down + 1 #increment counter for each watering
                        target_soil = self.target.getTarget("Soil") #get target soil moisture value

                        #run the pump until the timer hits 30 seconds or the current soil moisture is greater than the target
                        t = 0 #reset timer
                        while t <= 40 and global_vars.current_soil<int(target_soil):
                            global_vars.pumped = True #set pumped flag to true to indicate the pump occured
                            self.pi.write(self.pump, 1) #run pump
                            t = t + 1 #increase timer
                            time.sleep(1) #1 second delay
                        self.pi.write(self.pump, 0) #turn pump back off

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
