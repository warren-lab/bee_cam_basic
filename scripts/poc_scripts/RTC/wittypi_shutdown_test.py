"""
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

    # Grab the seconds from the WittyPi
    print("Seconds ",bcd_to_int(bus.read_byte_data(8,58)))
    print("Minutes ",bcd_to_int(bus.read_byte_data(8,59)))
    # Read RTC time from the WittyPi [IT IS ALREADY IN INT VALUES]
    time_list = []
    for i in range(58,65):

        time_list.append(bcd_to_int(bus.read_byte_data(8,i)))
    print(time_list)
    sec,min,hour,days,weekday,month,year= time_list
    # Python3 program for the above approach 
    print("seconds",sec)
    print(datetime(year+2000,month,days,hour,min,sec))
    print("Weekday",weekday)
    shutdown_time_min = 5 #minutes
    min_shutdown= min +shutdown_time_min
    shutdown_time_list =[sec,min_shutdown,hour,days,weekday]
    # Okay Schedule the Next Shutdown to be in 5 minutes...
    ## Set Minute  of Alarm2 -> 33 INT TO BCD
    ## Set Hour of Alarm2 -> 34 INT TO BCD
    ## Set Day of Alarm2 -> 35 INT TO BCD
    # ## Set Day of Week of Alarm2 -> 36, INT TO BCD
    print("Seconds?",sec)
    for count, val in enumerate(range(32,37)):
        # print(val, shutdown_time_list[count],BCDConversion(shutdown_time_list[count]))
        bus.write_byte_data(8,val,int_to_bcd(shutdown_time_list[count]))
        time.sleep(5)
    if bcd_to_int(bus.read_byte_data(8,40)) == 0:
        print("ALARM2 AKA SHUTDOWN: NOT TRIGGERED")
        shut_list = []
        for i in range(32,37):
            shut_list.append(bcd_to_int(bus.read_byte_data(8,i)))
        sec,min,hour,days,weekday =  shut_list
        print(datetime(year = year+2000, month = month, day=days,hour = hour,minute=min,second=sec))

    elif bcd_to_int(bus.read_byte_data(8,40)) == 1:
        print("ALARM2 AKA SHUTDOWN: TRIGGERED")
        print("Shutdown Time:\n")
        shut_list = []
        for i in range(32,37):
            shut_list.append(bcd_to_int(bus.read_byte_data(8,i)))
        sec,min,hour,days,weekday,month,year= time_list
        # Python3 program for the above approach 
        print(datetime(day=days,hour = hour,minute=min,second=sec))
    

    # SET STARTUP!
    start_time = datetime.now() + timedelta(minutes=20)
    start_time_list =[start_time.second,start_time.minute,start_time.hour,start_time.day,weekday_conv(datetime.weekday(start_time))]
    ##  # Using datetime.today()  INT
    for count, val in enumerate(range(27,32)):
        # print(val, shutdown_time_list[count],BCDConversion(shutdown_time_list[count]))
        bus.write_byte_data(8,val,int_to_bcd(start_time_list[count]))
        time.sleep(5)
    if bcd_to_int(bus.read_byte_data(8,39)) == 0:
        print("ALARM2 AKA STARTUP: NOT TRIGGERED")
        start_list = []
        for i in range(27,32):
            start_list.append(bcd_to_int(bus.read_byte_data(8,i)))
        sec,min,hour,days,weekday =  start_list
        print(datetime(year = year+2000, month = month, day=days,hour = hour,minute=min,second=sec))

    elif bcd_to_int(bus.read_byte_data(8,39)) == 1:
        print("ALARM2 AKA STARTUP: TRIGGERED")
        print("STARTUP Time:\n")
        start_list = []
        for i in range(27,32):
            start_list.append(bcd_to_int(bus.read_byte_data(8,i)))
        sec,min,hour,days,weekday,month,year= start_list
        # Python3 program for the above approach 
        print(datetime(day=days,hour = hour,minute=min,second=sec))


# # Given Number 
# N = 12
 
