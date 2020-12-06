# gardinette

# Introduction
Gardinette is a work-in-progress gardening automation platform. The goal of this project is to provide the "guts" of a single board computer running software which automates the gardening process, indoors or outdoors. Gardinette aims to accomplish this through a series of sensors and actuators which monitor and maintain growth conditions based on desired user parameters. 
# Download and Installation
Download the github command line tool if you do not already have it

```sudo apt-get install git```

Ensure your OS is up to date

1. ```sudo apt-get update```
2. ```sudo apt-get upgrade```

Download the github repository

3. ```git clone https://github.com/CadellVDH/gardinette.git```

Enter the gardinette directory

4. ```cd gardinette```

Install the requirements

5. ```sudo pip install -r requirements.txt```

# Usage
After installation, ensure the hardware device is powered on and connected to the internet. Also insure all peripherals are connected. 

First, start the pigpio daemon

```sudo pigpiod```

Next, test the hardware using the hardware diagnostics script, in the ```/CalibrationAndDiagnostics/``` directory

```python3 Hardware_Diagnostics.py```

After verifying that there are no issues with the hardware, you may choose to create a custom calibration table for your specific soil mixture. To do so, use the following command (also in the ```/CalibrationAndDiagnostics/``` directory:

```python3 Soil_Calibration.py```

*Note: this step is optional, and a default calibration table is already provided for you.

Now you can run the main gardening script. 

```Main.py```

Lastly, wait a few weeks to a few months (depending on your crop of choice), and enjoy the fruits of your labor!
