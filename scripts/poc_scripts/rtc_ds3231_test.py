import adafruit_ds3231
import time
import board
from datetime import datetime
# ## https://docs.circuitpython.org/projects/ds3231/en/latest/
# i2c = board.I2C()  # uses board.SCL and board.SDA
# rtc = adafruit_ds3231.DS3231(i2c)

# # Convert datetime to struct_time
struct_time = datetime.now()
print(struct_time)
# # For setting the time... system time to rtc...
# # rtc.datetime = datetime.now().timetuple()

# # # 
# t = rtc.datetime
# print(t)
# print(t.tm_hour, t.tm_min)

