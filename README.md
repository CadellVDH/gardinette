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
First, test the hardware using ```Hardware_Diagnostics.py```

```python3 Hardware_Diagnostics.py```

After verifying that there are no issues with the hardware, you may choose to create a custom calibration table for your specific soil mixture. To do so, use the following command:
```python3 Soil_Calibration.py```

