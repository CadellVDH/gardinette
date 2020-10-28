import Adafruit_DHT #temp and hunidity sensor
import board
import adafruit_ssd1306 #oled screen
import digitalio
import Adafruit_ADS1x15 #soil moisture sensor
from PIL import Image, ImageDraw, ImageFont

#The purpose of this script is to ensure that all peripheral hardware
#components are connected and functioning properly, prior to startup
#as well as during troubleshooting

#First test the OLED screen
try: #attempt to detect the OLED
    i2c = board.I2C() #these next few lines initialize the OLED
    oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c,reset=oled_reset) #specify oled we're using
except:
    print("Error occured while detecting board") #throw error if one occurs

try: #attempt to clear the OLED
    oled_reset = digitalio.DigitalInOut(board.D4) #reset oled
    oled.fill(0) #clear display
    oled.show() #update the display
except:
    print("Error occured while clearing board") #throw error if one occurs

try: #attempt to write to the oled
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



adc = Adafruit_ADS1x15.ADS1115() #store ADC class to variable

DHT_SENSOR = Adafruit_DHT.DHT22 #store temp and humidity sensor to  variable
DHT_PIN = 23 #set temp/hum pin
