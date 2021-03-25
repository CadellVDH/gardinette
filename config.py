#Config File for declaring and initializing global variables

def global_init():
    global current_temp #declare current temp global variable for use in threads
    global current_humidity #declare current humidity global variable for use in threads
    global current_soil #declare current soil global variable for use in threads

    #intialize all to 0
    current_temp = 0
    current_humidity = 0
    current_soil = 0 
