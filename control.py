#!/usr/bin/env python3
import os
import sys
import logging
from scripts.config import Config
from scripts.sensors import MultiSensor
from scripts.display import Display
from scripts.sensors import WittyPi
from scripts.sensors import DarkPeriod
from scripts.sensors import ShutdownTime
from picamera2 import Picamera2
from time import sleep
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
size = (config['imaging'].getint('w'), config['imaging'].getint('h'))
lens_position = config['imaging'].getfloat('lens_position')
img_count = 0


# set main and sub output dirs
main_dir = "/home/pi/data/"
date_folder = str(datetime.now().strftime("%Y-%m-%d"))
curr_date = os.path.join(main_dir, date_folder)
os.makedirs(curr_date , exist_ok=True)
## image data will save to a sub directory 'images'
path_image_dat = os.path.join(curr_date,'images')

os.makedirs(path_image_dat, exist_ok=True)
## sensor data will save to current data directory
path_sensor_dat = curr_date 


# Initialize the sensors...
## also initializes the csv file name timestamp

# sensors = MultiSensor(path_sensor_dat)
# Initialize the display
disp = Display()
disp.display_msg('Initializing', img_count)

# initialize wittypi shutdown
with WittyPi() as witty:
    shutdown_dt = witty.get_shutdown_datetime() 

# Configure logging
# log_file = "/home/pi/bee_cam/log.txt"
log_file = curr_date + "/log.txt"
print(log_file)
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("###################### NEW RUN ##################################")

try:
    camera = Picamera2()
    cam_config = camera.create_still_configuration({'size': size})
    camera.configure(cam_config)
    camera.exposure_mode = 'sports'
    camera.set_controls({"LensPosition": lens_position})
    camera.start()
    sleep(5)
except:
    disp.display_msg('Cam not connected', img_count)
    logging.error("Camera init failed")
    sys.exit()



# go to working dir
os.chdir(curr_date)
print('Imaging')
logging.info("Imaging...")

time_current = datetime.now()

cam_exception = threading.Event()
# dark_exception = threading.Event()
# time_exception = threading.Event()
# def sensor_data():
#     try:
#         # wait for event to be set
#         event.wait()
#         ## check the time and it will add the data if no exception raised
#         sensors.add_data(name,time_current)
#         # print(f"Sensor Data Acquired: {time_current_split}")
#         #print("Image acquired: ", time_current_split)
#     except DarkPeriod:
#         logging.info("Dark Period Exception Set Event")
#         dark_exception.set()
#     except ShutdownTime:
#         logging.info("Time for shutdown")
#         time_exception.set()
#     # # Save sensor data to csv immediately:
#     # sensors.append_to_csv()
def capture_image():
    try:
        time_current_split = str(time_current.strftime("%Y%m%d_%H%M%S"))
        camera.capture_file('images/'+name + '_' + time_current_split + '.jpg')
        # print(("Image acquired: %s", time_current_split))
        logging.info("Image acquired: %s", time_current_split)
        #print("Image acquired: ", time_current_split)

    except Exception as e:
        logging.error("Error in capture_image: %s".e)
        cam_exception.set()
MAX_RETRIES = 3
retry_count = 0
disp.display_msg('Starting Experiment', img_count)
logging.info('Starting Experiment')
time.sleep(3)
# Start timer for the sensors
curr_time = time.time()
while shutdown_dt >= datetime.now():
    try:
        disp.display_msg('Imaging!', img_count)
        # dark_exception = threading.Event()
        # time_exception = threading.Event()
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
        # print(time_current_split)
        # start the sensor thread and capture thread:
        # sensor_thread.start()
        capture_thread.start()

        # Main thread waits for the threads to finish
        ## first waits for this longer thread to complete first (3 seconds)
        capture_thread.join(timeout=3) 
        ## then will check if the sensor_thread is still alive and wait if needed 
        # sensor_thread.join() 

        # If darkperiod exception event is set
        # if dark_exception.is_set():
        #     raise DarkPeriod
        
        # if ShutdownTime is raised then it is time to shut the system down...
        # if time_exception.is_set():
            # raise ShutdownTime

        # If thread is still alive after 3 seconds, it's probably hung
        if capture_thread.is_alive():
            raise TimeoutError("Camera operation took too long!")
    
        img_count += 1
        retry_count = 0
       
        # if wanting a delay in saving sensor data:
        if (time.time()-curr_time) >= 60:
            logging.info("CPU "+str(psutil.cpu_percent(interval=1))+"%")
            # disp.display_msg('Update CSV', img_count)
            # sensors.append_to_csv()
            curr_time = time.time()
        sleep(1)
    except KeyboardInterrupt:
        # if len(list(sensors.data_dict.values())[0]) != 0:
        #     disp.display_msg('Update CSV', img_count) 
        #     # if list is not empty then add data...
        #     sensors.append_to_csv()
        #     time.sleep(3) 
        
        disp.display_msg('Interrupted', img_count)
        disp.disp_deinit()
        # sensors.sensors_deint()
        logging.info("KeyboardInterrupt")
        sys.exit()
    # except DarkPeriod:
    #     if len(list(sensors.data_dict.values())[0]) != 0:
    #         disp.display_msg('Update CSV', img_count) 
    #         # if list is not empty then add data...
    #         sensors.append_to_csv()
    #         time.sleep(3)  
    #     disp.display_msg('Dark Period Shutdown', img_count)
    #     sensors.sensors_deint()
    #     logging.info("DarkPeriod")
    #     with WittyPi() as witty:
    #         # print("Shutdown Time")
    #         witty.shutdown()
    #         witty.startup()
    #     sys.exit()

    except ShutdownTime:
        # if len(list(sensors.data_dict.values())[0]) != 0:
        #     disp.display_msg('Update CSV', img_count) 
        #     # if list is not empty then add data...
        #     sensors.append_to_csv()
        #     time.sleep(3) 
        # sensors.sensors_deint()
        disp.display_msg('Timed Shutdown', img_count)
        disp.disp_deinit() 
        with WittyPi() as witty:
            # print("Shutdown Time")
            witty.shutdown()
            witty.startup()
        sys.exit()

    except TimeoutError:
        retry_count += 1
        disp.display_msg('Cam Timeout!', img_count)
        logging.error("Camera operation timeout!")
        if retry_count >= MAX_RETRIES:
            disp.display_msg('Max retries reached!', img_count)
            logging.error("Max retries reached. Exiting...")
            disp.disp_deinit() 
            with WittyPi() as witty:
                # print("Shutdown Time")
                witty.shutdown()
                witty.startup()
            sys.exit()
        else:
            # Wait for a bit before attempting a retry
            sleep(2)
            continue
    except:
        disp.display_msg('Error', img_count)
        logging.exception("Error capturing image")
        disp.disp_deinit() 
        sys.exit()

