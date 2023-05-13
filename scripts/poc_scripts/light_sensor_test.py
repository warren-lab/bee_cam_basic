import board
import time
import adafruit_tsl2591
import sys
sys.path.append('../')
from sensors import LightSensor
# i2c = board.I2C()
# sensor = adafruit_tsl2591.TSL2591(i2c)
# read = True
class DarkPeriod(Exception):
    """Raised when the Lux value for 5 concurrent samples is below the threshold"""
    pass 

sensor = LightSensor()
time.sleep(2)
print("Sensor Initalized")
read = True
counter = 0
while read:
    try:
        lux = sensor.get_lux()
        print('Light: {0} lux'.format(round(lux,3)), f'Counter: {counter}')
        if sensor.get_lux() < 10:
            counter +=1
        else:
            counter = 0
        if counter > 5:
            raise DarkPeriod
        time.sleep(5)
    except KeyboardInterrupt:
        # run the sensor detit...
        sensor.sensors_deinit() 
        print("Done")
        read = False
    except DarkPeriod:
        print("NIGHT TIME")
        sensor.sensors_deinit() 
        read = False