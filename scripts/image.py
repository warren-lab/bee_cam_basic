import os
import sys
import logging
from .config import Config
from .display import Display
from .temp import TempSensor
from .light import LightSensor
from .sensordata import SensorData
from picamera2 import Picamera2
from time import sleep
from datetime import datetime
import threading

config = Config()

name = config['general']['name']    
size = (config['imaging'].getint('w'), config['imaging'].getint('h'))
lens_position = config['imaging'].getfloat('lens_position')
img_count = 0

sensors = SensorData()
light = LightSensor()
temp = TempSensor()
temp_data = {'temp': temp.temperature,
            'humid': temp.humidity}
light_data = light.data
metadata = temp_data | light_data
sensors.get_dict(metadata)
print(sensors.data_dict)
sensors.create_csv()
disp = Display()
disp.display_msg('Initializing', img_count)

# Configure logging
log_file = "/home/pi/bee_cam/log.txt"
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

# set output dir
path_images = "/home/pimport os
import sys
import logging
from .config import Config
from .display import Display
from .temp import TempSensor
from .light import LightSensor
from .sensordata import SensorData
from picamera2 import Picamera2
from time import sleep
from datetime import datetime
import threading

config = Config()

name = config['general']['name']    
size = (config['imaging'].getint('w'), config['imaging'].getint('h'))
lens_position = config['imaging'].getfloat('lens_position')
img_count = 0

sensors = SensorData()
light = LightSensor()
temp = TempSensor()
temp_data = {'temp': temp.temperature,
            'humid': temp.humidity}
light_data = light.data
metadata = temp_data | light_data
sensors.get_dict(metadata)
print(sensors.data_dict)
sensors.create_csv()
disp = Display()
disp.display_msg('Initializing', img_count)

# Configure logging
log_file = "/home/pi/bee_cam/log.txt"
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
print('Imaging')
logging.info("Imaging...")

def capture_image():
    time_current = datetime.now()
    time_current_split = str(time_current.strftime("%Y%m%d_%H%M%S"))
    camera.capture_file(name + '_' + time_current_split + '.jpg')
    logging.info("Image acquired: %s", time_current_split)
    #print("Image acquired: ", time_current_split)

MAX_RETRIES = 3
retry_count = 0


while True:
    try:
        disp.display_msg('Imaging!', img_count)

        # Start the camera capture in a separate thread
        capture_thread = threading.Thread(target=capture_image)
        capture_thread.start()

        # Wait for 3 seconds or until the thread finishes
        capture_thread.join(timeout=3)

        # If thread is still alive after 3 seconds, it's probably hung
        if capture_thread.is_alive():
            raise TimeoutError("Camera operation took too long!")
        
        img_count += 1
        retry_count = 0
        sleep(.7)
    except KeyboardInterrupt:
        disp.display_msg('Interrupted', img_count)
        logging.info("KeyboardInterrupt")
        sys.exit()
    except TimeoutError:
        retry_count += 1
        disp.display_msg('Cam Timeout!', img_count)
        logging.error("Camera operation timeout!")
        if retry_count >= MAX_RETRIES:
            disp.display_msg('Max retries reached!', img_count)
            logging.error("Max retries reached. Exiting...")
            sys.exit()
        else:
            # Wait for a bit before attempting a retry
            sleep(2)
            continue
    except:
        disp.display_msg('Error', img_count)
        logging.exception("Error capturing image")
        sys.exit()

