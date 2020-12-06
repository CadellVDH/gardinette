import Adafruit_ADS1x15 #soil moisture sensor
import csv #file output
import os #tools for working with the CLI
import numpy #math
from helpers import * #import helper functions


print("Now beginning soil sensor calibration...\n")
pins = pinout()

PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) #Get current directory for log files and for pin file
path = "%s/Calibration.csv" % PROJECT_DIRECTORY
if(os.path.isfile(path) == False):
    Calibration = open(path, "w+") #create file if none exists
    Calibration.close()

    with open('Calibration.csv', mode="w") as Calibration: #open calibration file
        Calibration_writer = csv.writer(Calibration, quotechar='"', quoting=csv.QUOTE_MINIMAL)
        Calibration_writer.writerow(['Moisture Percent', 'ADC Reading'])

        user_test = 0 #initialize user_test to 0 to start loop
        columnOne = [] #initialize arrays for calculating calibration coefficients
        columnTwo = []
        print("To perform the calibration, place the sensor into your calibration sample of known moisture content.")
        print("Type in your known moisture content, then hit [ENTER]")
        print("Repeat until you have tested all you samples. Then type 'end'")
        print("Be sure to wipe off the sensor between tests\n")
        while (user_test != 'end'):
            user_test = input("Enter the soil moisture percentage for the current test (or 'end' to end):")
            try:
                user_test = int(user_test)
            except:
                pass

            while(isinstance(user_test, int) == False and user_test != 'end'):
                user_test = input("Please enter only integers\nEnter the soil moisture percentage for the current test (or 'end' to end):")

            if (user_test != 'end'):
                columnOne.append(user_test) #store actual soil mositure content to column one
                columnTwo.append(adc_read(retry=10)) #read ADC and store to column two

                print("ADC Value: %f" % columnTwo[len(columnTwo)-1]) #print ADC value to console
                Calibration_writer.writerow([columnOne[len(columnOne)-1], columnTwo[len(columnTwo)-1]]) #write to csv

    print("Calibration.csv created!")

else:
    user_test = input("Would you like to create a new calibration table? \nWARNING! Doing so will overwrite any old calibration table. (Y/N)") #check if user would like to create a new calibration table
    while (user_test.lower() != "y" and user_test.lower() != "n"): #check that user input is valid
        print("Please enter only 'Y' or 'N'\n")
        print(user_test.lower())
        user_test = input("Would you like to create a new calibration table? \nWARNING! Doing so will overwrite any old calibration table. (Y/N)")

    if (user_test.lower() == "y"): #create new calibration table if one is desired

        with open('Calibration.csv', mode="w") as Calibration: #open calibration file
            Calibration_writer = csv.writer(Calibration, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            Calibration_writer.writerow(['Moisture Percent', 'ADC Reading'])

            user_test = 0 #initialize user_test to 0 to start loop
            columnOne = [] #initialize arrays for calculating calibration coefficients
            columnTwo = []
            print("To perform the calibration, place the sensor into your calibration sample of known moisture content.")
            print("Type in your known moisture content, then hit [ENTER]")
            print("Repeat until you have tested all you samples. Then type 'end'\n")
            print("Be sure to wipe off the sensor between tests\n")
            while (user_test != 'end'):
                user_test = input("Enter the soil moisture percentage for the current test (or 'end' to end):")
                try:
                    user_test = int(user_test)
                except:
                    pass

                while(isinstance(user_test, int) == False and user_test != 'end'):
                    user_test = input("Please enter only integers\nEnter the soil moisture percentage for the current test (or 'end' to end):")

                if (user_test != 'end'):
                    columnOne.append(user_test) #store actual soil mositure content to column one
                    columnTwo.append(adc_read(retry=10)) #read ADC and store to column two

                    print("ADC Value: %f" % columnTwo[len(columnTwo)-1]) #print ADC value to console
                    Calibration_writer.writerow([columnOne[len(columnOne)-1], columnTwo[len(columnTwo)-1]]) #write to csv

        print("Calibration.csv created!")

##Create linear regression from inputs
print("Now creating a linear regression from the data")
with open('Calibration.csv', 'r') as Calibration:
    lines = Calibration.readlines()
    columnOne = []
    columnTwo = []
    for line in lines:
        data = line.split(',')
        columnOne.append(data[0])
        columnTwo.append(data[1].rstrip('\n'))

columnOne.remove('Moisture Percent')
columnTwo.remove('ADC Reading')

actualMoisture = numpy.array(list(map(int, columnOne))) #get columns into numpy arrays
sensorValue = numpy.array(list(map(int, columnTwo)))

n = len(columnOne) #number of terms is equal to column length

sigXY = numpy.sum(numpy.multiply(actualMoisture, sensorValue)) #Sum of all x*y values for regression

sigX = numpy.sum(actualMoisture) #Sum of all x for regression

sigY = numpy.sum(sensorValue) #Sum of all y for regression

sigXSq = numpy.sum(numpy.power(actualMoisture, [2])) #Sum of all x^2 for regression

slope = (n*sigXY - sigX*sigY)/(n*sigXSq - sigX**2) #calculate slope

intercept = (sigY - slope*sigX)/n #calculate y intercept

print("Slope: %s\n" % slope)
print("Y intercept: %s\n" % intercept)

print("Regression complete!")
print("Now writing values to pinout file")


config_write('Calibration_Constants', 'SLOPE', slope) #write slope to ini file
config_write('Calibration_Constants', 'INTERCEPT', intercept) #write intercept to ini file
