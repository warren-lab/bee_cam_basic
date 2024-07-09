"""
Temperature control capability of wittypi testing

Registers:
50 -> temperature register (2 bytes)


Objective 1:
- Print output of the register and compare to the documentation.

Objective 2:
- Conver the register output to C or F




This script will attempt to shutdown the wittyPi by using our knowledge 
of the i2c and the smbus register...

As of 3/13/2024  this script is sucessfully in setting the shutdown time for the WittyPi.

NEXT STEPS:
- Setting Start Up Time:
- Shutdown Via Light Sensor Reading Fully integrate!
- Implement My own WittyPi4mini Package/Class
- 



OTHER INFO:

smbus2 -> https://github.com/kplindegaard/smbus2

Datasheets:
Witty Pi 4 Mini Main Datasheet:
    - https://www.uugear.com/doc/WittyPi4Mini_UserManual.pdf
THE RTC:
    - https://www.nxp.com/docs/en/data-sheet/PCF85063A.pdf
    - NOTE -> Weekdays go from 0 to 6...
        Ex: Weekday transformed from BCD to INT that is 3 corresponds to Wednesday

Sunday = 0
Monday =1
Tuesday =2
Wednesday = 3
Thursday=4
Friday=5
Saturday =6
"""
import sys
from smbus2 import SMBus
from datetime import datetime, timedelta
import time
## i2c Bus 1
## wittypi 4 mini is on
#### device -> x08

def int_to_bcd(value):
    """
    Convert an integer to its BCD representation.
    
    Args:
    - value: The integer value to convert (0-99).
    
    Returns:
    - The BCD representation as an integer.
    """
    return ((value // 10) << 4) | (value % 10)
def bcd_to_int(bcd):
    """
    Convert a BCD-encoded number to an integer. 
    """
    return ((bcd & 0xF0) >> 4) * 10 + (bcd & 0x0F)
def weekday_conv(val):
    """Takes input for the value of the weekday computed by
    the datetime module which sets Monday to 0...
    https://www.geeksforgeeks.org/weekday-function-of-datetime-date-class-in-python/


    """
    if val == 6:
        return 0
    else:
        return val + 1
with SMBus(1) as bus:

    b = bus.read_byte_data(8, 27)
    print(b)
    ## Power Mode? USB c 5v = 0, LDO regulator = 1
    powermode = bus.read_byte_data(8,7)
    print("Power Mode", powermode)
    ## The reason code for latest action
    latest_action = bus.read_byte_data(8,11)
    print("Input Voltage",latest_action)
    while True:
       try:
          # temperature of wittyPi
          temp = bus.read_byte_data(8,50)
          temp_f = temp*(9/5) + 32
          print(f"Temperature {round(temp,3)} C, {round(temp_f,3)} F")
          time.sleep(1)
       except:
          print("Interrupt")
          sys.exit()

    
