"""
This script will log and test the Witty Pis ability to automatically shutdown and startup

This script will be utilized in order to test WittyPi 4 hardware performance 
and mitigate in field failures of sensor systems.

This will be implemented to run on boot....

"""
import sys
import os
print(os.getcwd())
sys.path.append('/home/pi/bee_cam_basic')
from scripts.sensors import WittyPi
# initialize wittypi shutdown
with WittyPi() as witty:
    witty.shutdown_5min()
    witty.startup_10min()
