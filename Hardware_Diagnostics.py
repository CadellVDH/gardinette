import Adafruit_DHT #temp and hunidity sensor
import board #oled tools
import adafruit_ssd1306 #oled screen
import digitalio #oled tools
import Adafruit_ADS1x15 #soil moisture sensor
import os #tools for working with the CLI
from PIL import Image, ImageDraw, ImageFont #oled tools

#The purpose of this script is to ensure that all peripheral hardware
#components are connected and functioning properly, prior to startup
#as well as during troubleshooting

#Get current directory for log files and for pin file
PROJECT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
PATH = "%s/Pinout.ini" % PROJECT_DIRECTORY

#Look for pinout file and create one if it does not exist. Otherwise, write the file values to variables
if (os.path.isfile(PATH) == False): #check if file already exists
    Pinout = open(PATH, "w+") #create file if none exists
    Pinout.close()
    Config = ConfigParser()
    Config.add_section('Pin_Values')
    Config.add_section('Address_Values')
    Config.set('Pin_Values', 'FANONE', 13) #set value of FANONE in ini file
    Pinout.write("OLED_ADDRESS=0x3c\n")
    Pinout.write("FANONE=13\n")
    Pinout.write("FANTWO=12\n")
    Pinout.write("PUMP=17\n")
    Pinout.write("LIGHT=27\n")
    Pinout.write("FLOAT=22\n")
    Pinout.write("TEMP=23\n")
    Pinout.write("BUTTTONONE=6\n")
    Pinout.write("BUTTONTWO=16\n")
    Pinout.write("BUTTONTHREE=26\n")
    Pinout.close()
Pinout = open(PATH, "r")    
Pinout_String = Pinout.read()


#Initialize all pin variables
ADC_PIN=1
ADC_GAIN=1

#First test the OLED screen
print("Now testing the OLED screen...\n")
try: #attempt to detect the OLED
    print("Attempting to detect OLED...\n")
    oled_reset = digitalio.DigitalInOut(board.D4) #reset oled
    i2c = board.I2C() #these next few lines initialize the OLED
    oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c,reset=oled_reset) #specify oled we're using
    print("OLED detected\n")
except:
    print("Error occured while detecting board") #throw error if one occurs

try: #attempt to clear the OLED
    print("Attempting to clear the OLED...\n")
    oled.fill(0) #clear display
    oled.show() #update the display
    print("OLED cleared\n")
except:
    print("Error occured while clearing board") #throw error if one occurs

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
    oled.show()
except:
    print("Error occured while writing text to the OLED")

user_test = input('Was the text "Gardinette!" shown? (Y/N)') #ask user to verify real world
while (user_test != "Y" and user_test != "N"):
    print('Please enter only "Y" or "N"')
    user_test = input('Was the text "Gardinette!" shown? (Y/N)')
if (user_test == "N"):
    print("Error occured while writing to OLED screen\n")
else:
    print("OLED tests have succeeded\n")

print("All OLED tests have been completed\n")

#Next test the ADC/moisture sensor
print("Now testing the ADC/Moisture Sensor\n")
adc = Adafruit_ADS1x15.ADS1115() #store ADC class to variable
print("Attempting to read value from ADC\n")
try:
    ADCvalue = adc.read_adc(ADC_PIN, gain=ADC_GAIN) #ATTEMPT TO READ ADC
    print("ADC value: %f\n" % ADCvalue)
    print("ADC succesffully read")
except:
    print("Error occured while reading ADC value")

print("All ADC tests have been completed\n")

#Test the temperature and humidity sensor
print("Now testing the temperature and humidity sensor\n")
DHT_SENSOR = Adafruit_DHT.DHT22 #store temp and humidity sensor to  variable
DHT_PIN = 23 #set temp/hum pin
try:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN) #attempt to read temp and humidity sensor
    print("Temp: %f\n" % temperature)
    print("Humidity: %f\n" % humidity)
    print("Temp and humidity tests have succeeded\n")
except:
    print("An error occured while reading the temperature or humidity\n")

print("All temperature and humidity tests have been completed\n")

print("All tests have been completed\n")
