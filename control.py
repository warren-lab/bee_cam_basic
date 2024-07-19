#!/usr/bin/env python3
import os
import sys
import signal
import logging
from scripts.config import Config
from scripts.sensors import MultiSensor
from scripts.sensors import Display
from scripts.sensors import WittyPi
from scripts.sensors import DarkPeriod
from scripts.sensors import ShutdownTime
from picamera2 import Picamera2
from time import sleep
from time import time
from datetime import datetime
import threading
import time
import psutil
"""
Image2 is the current version of the imaging script for writing the sensor data to csv


Functionality:
- Saves Sensor data to dictionary and after [30 seconds] appends to csv. 
It is important to note that if you kill the script that any data that has been saved 
into this dictionary will immediately be appended to the csv file and the last recorded images will also be written.
- The sensor and imaging timestamps are in sync and this can be validated from the log file.

TO DO:
- Finalize Solar Testing and Verify with the voltage difference thing to make sure that our readings are good for the single cell
- Then attempt to test with the multi cell 10050mah module...
- Provide error handling for solar and voltage/power of pi...
    -  Purchase a device that will do this...

- Need to implement the night time imaging threshold based on the light sensor
- Battery data need to log this data and write...
- Keep pi and witty pi on for long duration...
- Determine RTC alternative...
- add in the GPS Sensor Functionality





"""



def shutdown_to_sleep():
    """ This method signals a shutdown time to the
    WittyPi that is 5 minutes from current time. 

    This shutdown is signaled by either dark period, or 
    target time is reached (right now its 5:30pm).

    The bashscript BeforeShutdown.sh will be automatically executed right before the WittyPi 
    shuts down. So this method will just send the wittyPi the shutdown time.

    """

config = Config()

name = config['general']['name']
start_1 = config['imaging']['startup']
end_1 = config['imaging']['shutdown'] 
size = (config['imaging'].getint('w'), config['imaging'].getint('h'))
lens_position_cfg = config['imaging'].getfloat('lens_position')
img_count = 0
test_yn = config['general']['test']

# set main and sub output dirs
main_dir = "/home/pi/data/"
date_folder = str(datetime.now().strftime("%Y-%m-%d"))
curr_date = os.path.join(main_dir, date_folder)
os.makedirs(curr_date , exist_ok=True)
## image data will save to a sub directory 'images'
path_image_dat = os.path.join(curr_date,'images')

os.makedirs(path_image_dat, exist_ok=True)

# Initialize display
disp = Display()
disp.display_msg('Initializing', img_count)

# initialize wittypi shutdown
with WittyPi() as witty:
    shutdown_dt = witty.shutdown_startup(start_1,end_1) 

# Configure logging
# log_file = "/home/pi/bee_cam/log.txt"
log_file = curr_date + "/log.txt"
print(log_file)
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("###################### NEW RUN ##################################")
# set the pucamera logger
picam_log = logging.getLogger('picamera2')
picam_log.setLevel(logging.DEBUG)

try:
    camera = Picamera2()
    cam_config = camera.create_still_configuration({'size': size})
    camera.configure(cam_config)
    camera.exposure_mode = 'sports'
    camera.set_controls({"LensPosition": lens_position_cfg})
    camera.start()
    sleep(5)
except:
    disp.display_msg('Cam not connected', img_count)
    logging.error("Camera init failed")
    sleep(5)
    disp.clear_display()
    disp.disp_deinit()
    sys.exit()

# go to working dir
os.chdir(curr_date)

if test_yn == 'y':
    disp.display_msg('TEST MODE', img_count)
    if not os.path.exists('test_imgs'):
        os.mkdir('test_imgs')
    os.chdir('test_imgs')
    import numpy as np
    lp_list = np.arange(0, 2.75, 0.25)
    img_count = len(lp_list)
    for lp in lp_list:
        camera.set_controls({"LensPosition": lp})
        camera.capture_file(f'lp_{lp}.jpg')
        sleep(0.3)
        img_count -= 1
        disp.display_msg('TEST MODE', img_count)
    disp.display_msg('Test complete', img_count)
    os.chdir(curr_date)
    camera.set_controls({"LensPosition": lens_position_cfg})

print('Imaging')
logging.info("Imaging...")
img_count = 0

time_current = datetime.now()

cam_exception = threading.Event()

# def capture_image():
#     global last_capture_time

#     try:
#         time_current_split = str(time_current.strftime("%Y%m%d_%H%M%S"))
#         camera.capture_file('images/'+name + '_' + time_current_split + '.jpg')
#         # print(("Image acquired: %s", time_current_split))
#         logging.info("Image acquired: %s", time_current_split)
#         #print("Image acquired: ", time_current_split)

#     except Exception as e:
#         logging.error("Error in capture_image: %s".e)
#         cam_exception.set()

last_capture_time = time.time() - 1

def capture_image():
    global last_capture_time
    global img_count
    
    try:
        current_time = time.time()
        
        if current_time - last_capture_time >= 1:
            time_current = datetime.now()
            time_current_split = str(time_current.strftime("%Y%m%d_%H%M%S"))
            camera.capture_file('images/' + name + '_' + time_current_split + '.jpg')
            logging.info("Image acquired: %s", time_current_split)

            last_capture_time = current_time
            img_count += 1
        else:
            logging.info("Skipping capture to ensure one image per second rule")

    except Exception as e:
        logging.error("Error in capture_image: %s", e)
        cam_exception.set()


MAX_RETRIES = 6
retry_count = 0
disp.display_msg('Starting Experiment', img_count)
logging.info('Starting Experiment')
sleep(1)

# SET PID
def sig_handler(signum, frame):
    """Signal Handler for If SIGTERM signal"""
    disp.display_msg('Script Killed!', img_count)
    sleep(5)
    disp.clear_display()
    disp.disp_deinit()
    logging.info("Control Script Killed!")
    sys.exit(0)

# pid = os.getpid()
signal.signal(signal.SIGTERM,sig_handler)

# Start timer for the sensors
curr_time = time.time()
while True:
    try:
        disp.display_msg('Imaging!', img_count)
        # Create the Event
        event =  threading.Event()
        # set the event
        event.set()
        # develop two threads, one for sensors and one for images
        # sensor_thread = threading.Thread(target = sensor_data)
        capture_thread = threading.Thread(target=capture_image)
        ## get the current time
        time_current = datetime.now()
        time_current_split = str(time_current.strftime("%Y%m%d_%H%M%S"))

        # start the sensor thread and capture thread:
        capture_thread.start()

        # Main thread waits for the threads to finish
        ## first waits for this longer thread to complete first (3 seconds)
        capture_thread.join(timeout=2) 

        # If thread is still alive after 3 seconds, it's probably hung
        if capture_thread.is_alive():
            raise TimeoutError("Camera operation took too long!")
        
        if shutdown_dt <= datetime.now():
            raise ShutdownTime
        
        retry_count = 0
       
    except KeyboardInterrupt:
        disp.display_msg('Interrupted', img_count)
        time.sleep(5)
        logging.info("KeyboardInterrupt")
        disp.clear_display()
        disp.disp_deinit()
        sys.exit()

    except TimeoutError:
        retry_count += 1
        disp.display_msg('Cam Timeout!', img_count)
        logging.error("Camera operation timeout!")
        if retry_count >= MAX_RETRIES:
            disp.display_msg('Max retries reached!', img_count)
            logging.error("Max retries reached. Exiting...")
            sleep(5)
            disp.clear_display()
            disp.disp_deinit() 
            with WittyPi() as witty: # set shutdown and startup
                witty.shutdown()
                witty.startup_10min()
            sys.exit()
        elif MAX_RETRIES == 1:
            logging.info("First Retry...Long 10s Delay")
            sleep(10) # Testing long delay after first instance...
        else:
            # Wait for a bit before attempting a retry
            sleep(2)
            continue
    except ShutdownTime:
        disp.display_msg('Timed Shutdown', img_count)
        sleep(10)
        with WittyPi() as witty: # set shutdown and startup
            witty.shutdown()
            # witty.startup() # Timed startup set at start 
        sleep(5)
        disp.clear_display()
        disp.disp_deinit() 
        sys.exit()
    except:
        disp.display_msg('Error', img_count)
        logging.exception("Error capturing image")
        sleep(5)
        disp.clear_display()
        disp.disp_deinit() 
        sys.exit()



