# gardinette

# Introduction
Gardinette is a work-in-progress gardening automation platform. The goal of this project is to provide the "guts" of a single board computer running software which automates the gardening process, indoors or outdoors. Gardinette aims to accomplish this through a series of sensors and actuators which monitor and maintain growth conditions based on desired user parameters. 
# Download and Installation
Download the github repository
1. ```bash git clone https://github.com/CadellVDH/gardinette.git```
Ensure your OS is up to date
2. ```bash sudo apt-get upgrade```
3. ```bash sudo apt-get update```
Install the requirements
4. ```bash sudo pip install -r requirements.txt```

# Usage
After installation, ensure the hardware device is powered on and connected to the internet. Also insure all peripherals are connected. 
First, test the hardware using ```Hardware_Diagnostics.py```

```bash python3 Hardware_Diagnostics.py```

If no errors occur, proceed to running the main script
(To be written)
