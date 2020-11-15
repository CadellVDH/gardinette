import Adafruit_ADS1x15 #soil moisture sensor

Config = ConfigParser()
if (os.path.isfile(PATH) == False): #check if file already exists
    Pinout = open(PATH, "w+") #create file if none exists
    Pinout.close()
    Config.add_section('Pin_Values')
    Config.add_section('Address_Values')
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
