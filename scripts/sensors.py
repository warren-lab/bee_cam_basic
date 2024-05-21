## general imports
from datetime import datetime,timedelta
import os
import sys
import time
import socket
import board
## data
from csv import DictWriter
## temperature data...
import adafruit_si7021
## light sensor data
import adafruit_tsl2591
## GPS

## RTC

## WittyPi
from smbus2 import SMBus
## Display
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


"""
Goal is to make a main sensor class and then 2 child classes for the individual sensors

- So these sensors will have all of the 
"""

# Initialized some exceptions that will be utilized as well
class DarkPeriod(Exception):
    """Raised when the Lux value for 5 concurrent samples is below the threshold"""
    pass 

class ShutdownTime(Exception):
    """Raised when the shutdown time is reached. This time will change on reboot"""
    pass

class WittyPi():
    """
    Sensor class specific to the UUGear WittyPi 4 Mini

    Current Issues:
        -  The current issue is that we are unable to get the correct RTC time on the pi when we want to sync
        - The solution for this is to instead utilize the GPS RTC first to write to the system time and then write the sytstem time to the WittyPi. That way we have complete accuracy...
            - we could use the other RTC but the wittypi has more robust functionality for startup and shutdown based on the datetime and ensuring the time accuracy is important
        - Do some troubleshooting in order to check the differences in the system, RTC from GPS and the wittypi RTC

    Upon initalizing this sensor when the board is booted the GPS Sensor RTC will be written to the WittyPi. This should be done by using a BashScript...
    
    Weekdays:
    Sunday = 0
    Monday =1
    Tuesday =2
    Wednesday = 3
    Thursday=4
    Friday=5
    Saturday =6



    TODO->

    First need to create an set SHUTDOWN METHOD! AND THEN WE GET THE TIME

    THEN WHEN WE OPEN THE WITTYPI again if we need a new fresh object which is likely then that means that we will need to also then 
    input that shutdown desired time... and so once that time has hit then we will add an extra 5 min to it and that is what we will send to the registers...


    """
    def __init__(self, bus_num= 1):
        self._bus_num = bus_num
        self._bus = None
        # Shutdown
        self._shutdown_datetime = ""
        self._time_to_shutdown = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

        # Startup
        self._startup_datetime = ""
        self._time_to_startup = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)


    def __enter__(self):
        """return the SMBus object"""
        self._bus = SMBus(self._bus_num)
        return self
    def __exit__(self,exception_type, exception_value, exception_traceback):
        """close the bus"""
        self._bus.close()
    
    def int_to_bcd(self,value):
        """
        Convert an integer to its BCD representation.
        
        Args:
        - value: The integer value to convert (0-99).
        
        Returns:
        - The BCD representation as an integer.
        """
        return ((value // 10) << 4) | (value % 10)
    def bcd_to_int(self, bcd):
        """
        This method converts BCD-encoded value to an integer.
        """
        return ((bcd & 0xF0) >> 4) * 10 + (bcd & 0x0F)
    def weekday_conv(self, val):
        """Takes input for the value of the weekday computed by
        the datetime module which sets Monday to 0...
        https://www.geeksforgeeks.org/weekday-function-of-datetime-date-class-in-python/
        """
        if val == 6:
            return 0
        else:
            return val + 1
    
    def get_current_time(self):
        """
        Get the current time on the WittyPi 4 mini
        
        datetime.now() could be used but for redundancy sake this method will be used just in case. Regardless the WittyPi should have a similar if not the same time as datetime.now()
        """
        time_list = []
        for i in range(58,65):

            time_list.append(self.bcd_to_int(self._bus.read_byte_data(8,i)))
        print(time_list)
        sec,min,hour,days,weekday,month,year= time_list
        curr_time = datetime(year = year+2000, month = month, day=days,hour = hour,minute=min,second=sec)
        return curr_time
    def get_shutdown_datetime(self):
        """
        get the datetime for when shutdown will occur
        sets the shutdown to occur at 8pm (TEST CASE 9:30 pm)

        The actual shutdown executed by the shutdown script will happen at 9:35pm to give a bit more buffer
        """
        curr_time = self.get_current_time()
        # Set the shutdown time for today (will be 8pm normally!)
        self._shutdown_datetime= curr_time.replace(hour = 20,minute = 0, second = 0)# amount of time until shutdown (at least 3 minutes)
        print(self._shutdown_datetime)
        print(self._shutdown_datetime >= datetime.now())
        return self._shutdown_datetime
    def get_shutdown_datetime_5min(self):
        """
        get the datetime for when shutdown will occur
        
        this is a test case that has shutdown occur in 5 minutes time
        """
        curr_time = self.get_current_time()
        self._time_to_shutdown = timedelta(minutes=5) # amount of time until shutdown (at least 3 minutes)
        self._shutdown_datetime = curr_time +self._time_to_shutdown # time that system will shutdown
        print(self._shutdown_datetime)
        print(self._shutdown_datetime >= datetime.now())
        return self._shutdown_datetime

    def shutdown(self):
        """
        Shutdown method for communicating to the WittyPin 4 mini
        to shutdown at 7pm...
        
        Uses registers 32-36
        
        shutdown is triggered when greater or equal to shutdown time... so when reaching shutdown... then add 5min to current time
        and signal the shutdown
        
        shutdown at 7:05pm or 9:35pm
        """
        # with SMBus(1) as bus:
        # Read RTC time from the WittyPi [IT IS ALREADY IN INT VALUES]st
        shutdown_datetime = self.get_current_time()
        # Add a 5 minute buffer to the shutdown time of 7pm or (9:30pm if TEST)
        shutdown_datetime += timedelta(minutes=5)
        print("shutdown time:",shutdown_datetime)
        # Add five minutes to the shutdown time just in case...
        shutdown_time_list = [shutdown_datetime.second,shutdown_datetime.minute ,shutdown_datetime.hour,shutdown_datetime.day,self.weekday_conv(datetime.weekday(shutdown_datetime))]
        shutdown_year = shutdown_datetime.year
        shutdown_month = shutdown_datetime.month
        for count, val in enumerate(range(32,37)):
        # print(val, shutdown_time_list[count],BCDConversion(shutdown_time_list[count]))
            self._bus.write_byte_data(8,val,self.int_to_bcd(shutdown_time_list[count]))
            time.sleep(5)
        if self.bcd_to_int(self._bus.read_byte_data(8,40)) == 0:
            print("ALARM2 AKA SHUTDOWN: NOT TRIGGERED")
            shut_list = []
            for i in range(32,37):
                shut_list.append(self.bcd_to_int(self._bus.read_byte_data(8,i)))
            sec,min,hour,days,weekday =  shut_list
            print(datetime(year = shutdown_year, month = shutdown_month, day=days,hour = hour,minute=min,second=sec))

        elif self.bcd_to_int(self._bus.read_byte_data(8,40)) == 1:
            print("ALARM2 AKA SHUTDOWN: TRIGGERED")
            print("Shutdown Time:\n")
            shut_list = []
            for i in range(32,37):
                shut_list.append(self.bcd_to_int(self._bus.read_byte_data(8,i)))
            sec,min,hour,days,weekday= shut_list
            # Python3 program for the above approach 
            print(datetime(year = shutdown_year, month = shutdown_month, day=days,hour = hour,minute=min,second=sec))
        
    def shutdown_5min(self):
        """
        Shutdown method for communicating to the WittyPin 4 mini
        to shutdown in 5 minutes time from the current time
        
        Uses registers 32-36
        
        shutdown is triggered when greater or equal to shutdown time... so when reaching shutdown... then add 5min to current time
        and signal the shutdown
        
        """
        # with SMBus(1) as bus:
        # Read RTC time from the WittyPi [IT IS ALREADY IN INT VALUES]st
        shutdown_datetime = self.get_current_time() # 
        shutdown_datetime += timedelta(minutes=5)
        # Add five minutes to the shutdown time just in case...
        shutdown_time_list = [shutdown_datetime.second,shutdown_datetime.minute ,shutdown_datetime.hour,shutdown_datetime.day,self.weekday_conv(datetime.weekday(shutdown_datetime))]
        shutdown_year = shutdown_datetime.year
        shutdown_month = shutdown_datetime.month
        for count, val in enumerate(range(32,37)):
        # print(val, shutdown_time_list[count],BCDConversion(shutdown_time_list[count]))
            self._bus.write_byte_data(8,val,self.int_to_bcd(shutdown_time_list[count]))
            time.sleep(5)
        if self.bcd_to_int(self._bus.read_byte_data(8,40)) == 0:
            print("ALARM2 AKA SHUTDOWN: NOT TRIGGERED")
            shut_list = []
            for i in range(32,37):
                shut_list.append(self.bcd_to_int(self._bus.read_byte_data(8,i)))
            sec,min,hour,days,weekday =  shut_list
            print(datetime(year = shutdown_year, month = shutdown_month, day=days,hour = hour,minute=min,second=sec))

        elif self.bcd_to_int(self._bus.read_byte_data(8,40)) == 1:
            print("ALARM2 AKA SHUTDOWN: TRIGGERED")
            print("Shutdown Time:\n")
            shut_list = []
            for i in range(32,37):
                shut_list.append(self.bcd_to_int(self._bus.read_byte_data(8,i)))
            sec,min,hour,days,weekday= shut_list
            # Python3 program for the above approach 
            print(datetime(year = shutdown_year, month = shutdown_month, day=days,hour = hour,minute=min,second=sec))
    def startup(self):
        """
        This method sets the startup time registers on the WittyPi 4 mini 
        
        In this case it sets the start up time to be 7am 


        """
        # SET STARTUP!
        ## get the current time
        start_time = self.get_current_time() 
        ## get the time for the next day, as the experiment will start on button click initally but we want to assign every single next boot...
        start_time = start_time + timedelta(days=1)
        ## now for the start time need to reassign the actual hour,min,second for the experimental start
        start_time =  start_time.replace(hour=6,minute=0,second=0)
        print("StartUp Time:",start_time)
        start_time_list =[start_time.second,start_time.minute,start_time.hour,start_time.day,self.weekday_conv(datetime.weekday(start_time))]
        year = start_time.year
        month = start_time.month
        ##  # Using datetime.today()  INT
        for count, val in enumerate(range(27,32)):
            # print(val, shutdown_time_list[count],BCDConversion(shutdown_time_list[count]))
            self._bus.write_byte_data(8,val,self.int_to_bcd(start_time_list[count]))
            time.sleep(5)
        if self.bcd_to_int(self.int_to_bcd(self._bus.read_byte_data(8,39))) == 0:
            print("ALARM2 AKA STARTUP: NOT TRIGGERED")
            start_list = []
            for i in range(27,32):
                start_list.append(self.bcd_to_int(self._bus.read_byte_data(8,i)))
            sec,min,hour,days,weekday =  start_list
            print(datetime(year = year+2000, month = month, day=days,hour = hour,minute=min,second=sec))

        elif self.bcd_to_int(self._bus.read_byte_data(8,39)) == 1:
            print("ALARM2 AKA STARTUP: TRIGGERED")
            print("STARTUP Time:\n")
            start_list = []
            for i in range(27,32):
                start_list.append(self.bcd_to_int(self._bus.read_byte_data(8,i)))
            sec,min,hour,days,weekday= start_list
            # Python3 program for the above approach 
            print(datetime(day=days,hour = hour,minute=min,second=sec))
            
    def startup_5min(self):
        # SET STARTUP!
        start_time = self.get_current_time() + timedelta(minutes=10)
        start_time_list =[start_time.second,start_time.minute,start_time.hour,start_time.day,self.weekday_conv(datetime.weekday(start_time))]
        year = start_time.year
        month = start_time.month
        ##  # Using datetime.today()  INT
        for count, val in enumerate(range(27,32)):
            # print(val, shutdown_time_list[count],BCDConversion(shutdown_time_list[count]))
            self._bus.write_byte_data(8,val,self.int_to_bcd(start_time_list[count]))
            time.sleep(5)
        if self.bcd_to_int(self.int_to_bcd(self._bus.read_byte_data(8,39))) == 0:
            print("ALARM2 AKA STARTUP: NOT TRIGGERED")
            start_list = []
            for i in range(27,32):
                start_list.append(self.bcd_to_int(self._bus.read_byte_data(8,i)))
            sec,min,hour,days,weekday =  start_list
            print(datetime(year = year+2000, month = month, day=days,hour = hour,minute=min,second=sec))

        elif self.bcd_to_int(self._bus.read_byte_data(8,39)) == 1:
            print("ALARM2 AKA STARTUP: TRIGGERED")
            print("STARTUP Time:\n")
            start_list = []
            for i in range(27,32):
                start_list.append(self.bcd_to_int(self._bus.read_byte_data(8,i)))
            sec,min,hour,days,weekday= start_list
            # Python3 program for the above approach 
            print(datetime(day=days,hour = hour,minute=min,second=sec))

        
    def shutdown_startup(self):
        """
        Performs both a shutdown and then subsequently a startup without closing the SMBus
        """
        pass

class Sensor:
    # dictionary of sensor data intrinsict for each sensor type
    data_dict ={} 
    # Initialized the time domain for this dictionary
    data_dict['time'] = []
    # Initialized the image file key for this dictionary
    data_dict['image_filename'] = []

    # Create library object using our Bus I2C port
    i2c = board.I2C()  # uses board.SCL and board.SDA
    def __init__(self, device = None):

        ## name of sensor
        self.sensor_device = device

    def get_data(self,sensor_type):
        """
        Depending on the child class sensor device get_data will be
        used in order to grab the current sensor reading from the sensor.
        """
        data = getattr(self.sensor_device,sensor_type) # object, attribute
        return data
    def add_data(self,sensor_type):
        """
        Add data into the dictionary under the key of the sensor type

        Also returns the current data that was recieved in case that wants to be examined
        """
        data = self.get_data(sensor_type)
        ## check to see if the key exists first and if it does then add to it
        if sensor_type not in self.data_dict.keys():
            self.data_dict[sensor_type] = [data]
        ## if key doesn't exist then create
        else:
            self.data_dict[sensor_type].append(data)
            
        return data
    def display(self):
        """
        Display the sensor dictionary
        """
        print("Sensor Data")
        d = self.data_dict
        print(d)
    def reset_dict(self):
        """
        reset the dictionary
        """
        return
    def sensor_deinit(self):
        self.i2c.deinit() 

    # def write_csv(self):
    #     """
    #     Write the saved sensor data to file

    #     This can be used in the case where you want specific information fo
    #     """


# Temperature and Relative Humidity Sensor 
class TempRHSensor(Sensor):
    def __init__(self):
        super().__init__(adafruit_si7021.SI7021(self.i2c))

        # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
        ## sensor types:
        self.sensor_types = ['temperature','relative_humidity']
    def temp_rh_data(self):
        """
        gets the temperature and adds it to the dictionary but also 
        returns the temperature 
        """
        ## adds data to the dictionary
        ### also provides current data point
        data1 = self.add_data(self.sensor_types[0])
        data2 = self.add_data(self.sensor_types[1])
        ## update the dictionary

        return data1,data2
#  Light Sensor
class LightSensor(Sensor):
    """
    Need to enable error handling so that if the sensor is not connecting we can continue
    with the remaining sensors and the imaging...
    """
    def __init__(self):
        super().__init__(adafruit_tsl2591.TSL2591(self.i2c))
        #self.number_of_reads = config['Light'].getint('number_of_reads')
        #self.read_dt = config['Light'].getfloat('read_dt')
        self.sensor_device.gain = adafruit_tsl2591.GAIN_MED
        self.sensor_device.integration_time = adafruit_tsl2591.INTEGRATIONTIME_200MS
        self.sensor_types = ['lux','visible','infrared','full_spectrum']

        # set the light sensor lux threshold (https://www.engineeringtoolbox.com/light-level-rooms-d_708.html)
        self._lux_thr = 10
        self.counter = 0 # interal counter for this sensor for how many readings are below threshold (max 5)
    
    def light_data(self):
        """
        gets the temperature and adds it to the dictionary but also 
        returns the temperature 
        """
        # get light data
        lux,viz,ir,full = self.sensor_types
        # prior to adding the data to the dictionary need to verify that the lux in in range
        if self.get_lux() < 10:
            self.counter +=1
        else:
            self.counter = 0
        if self.counter > 5:
            raise DarkPeriod

        ## adds data to the dictionary
        ### also provides current data point
        data1 = self.add_data(lux)
        data2 = self.add_data(viz)
        data3 = self.add_data(ir)
        data4 = self.add_data(full)
        ## update the dictionary
        return data1,data2,data3, data4
    def get_lux(self):
        """
        
        check to see if the lux over several measurements is under the threshold
        if the lux is under the threshold for 5 measurements (maybe have it be more or less?)
        then will send signal to kill data collection process
        """

        return self.get_data(self.sensor_types[0])
    
# class Battery(Sensor):
#     """
#     Sensor class specific to the Adafruit MAX17048 Lipo Battery Fuel Gauge

#     Current Issues:
#      - Current Charge Estimate
#      - Issue with calibration of the battery  

#     """
class GPS(Sensor):
    """
    Sensor class specific to the Adafruit Mini GPS PA1010D Module

    Current Issues:
     - Need to essentially enable the write of the RTC time from the GPS to the Pi System Time
     - Afterwar

    """
class RTC(Sensor):
    """
    Sensor class specific to the Adafruit DS3231 Precision RTC - STEMMA QT

    This sensor will act as a back up RTC as the supercapacitor on the WittyPi 4 Mini will not 
    maintain time while powered off for a long period. So, during transit of the sensor system this
    RTC will be utilized in place of the WittyPi which will be disconnected from the power supply.

    Upon set up of the sensor system in the field this sensor is the first one that should be used ensuring
    the time on the device is calibrated.

    https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi/set-rtc-time
    - we needed to use this tutorial in order to get rid of the fake-hwclock functionality that the Raspberry Pi
    has built in when ther eis no RTC... What this means is that we are then going to essentially override this 
    and implement the DS3231 sensor in its place as a reliable RTC...

        - NOTE -> Witty Pi also has RTC... so will need to detemine conflicts with that... and ensure that the wittyPi
        gets calibrated by the system. 
        - NOTE -> Witty Pi essentially needs to be same time as RTC/System because it will act as power managment and 
        ensure the start up and shutdown times...

    After setting the DS3231 to be the RTC for the Pi then we needed to anable the network time protocol
    synchronization
        - enable NTP sync
        ```sudo timedatectl set-ntp true```
        
        - update system time
        ```sudo systemctl restart systemd-timesyncd```

        - finally check the current date
        ```date```
    
    After performing all of these steps this sensor will not be integrated into 
    the Sensor stack in the control script as it is already running in the background
    """


# class Monitor(Sensor):
#     """
#     Sensor subclass specfic to a 128x64 Oled Display

#     Sensor Source -> https://www.amazon.com/Hosyond-Display-Self-Luminous-Compatible-Raspberry/dp/B09C5K91H7/ref=cm_cr_arp_d_product_top?ie=UTF8&th=1

#     Methods:
#     - show_system_stat()
#         Displays the current system status
#     - 



#     Display showcasing Pi information and status
    
#     SOURCE -> https://github.com/adafruit/Adafruit_CircuitPython_SSD1306/tree/main
#     """
#     def __init__(self, width, height): ## when calling function input the width and height
#         super().__init__(adafruit_ssd1306.SSD1306_I2C(width,height, self.i2c))
#         ## dimensions
#         self._width = width
#         self._height = height
#         ## font
#         self._font = ImageFont.load_default()
#         ##
#         self._enabled = True
#         # get ip address
#         self._ip = self.get_ip_address()
        
#         ## initialize board to clear
#         self.sensor_device.fill(0)
#         self.sensor_device.show()

#     def display_time(self):
#         if not self._enabled:
#             return

#         image = Image.new('1', (self._width, self._height))
#         draw = ImageDraw.Draw(image)
        
#         # Clear the image buffer
#         draw.rectangle((0, 0, self._width, self._height), outline=0, fill=0)

#         # Get the current time
#         current_time = time.strftime('%H:%M:%S')
        
#         # Draw the time on the image
#         draw.text((0, 1), current_time, font=self._font, fill=255)

#         # Display the image
#         self.image(image)
#         self.show()

#     def display_msg(self, status, img_count=1):
#         if not self._enabled:
#             return

#         msg = [f'{status}', 
#                 time.strftime('%H:%M:%S'),
#                 f'Img count: {img_count}',
#                 f'IP: {self._ip}']

        
#         image = Image.new('1', (self._width, self._height))
#         draw = ImageDraw.Draw(image)
        
#         # Clear the image buffer
#         draw.rectangle((0, 0, self._width, self._height), outline=0, fill=0)
#         #_, font_height = self.font.getsize('Sample Text')
#         x, y = 0, 0
#         for item in msg:
#             draw.text((x, y), item, font=self._font, fill=255)
#             y += 14
        
#         self.sensor_device.image(image)
#         self.sensor_device.show()
#     def clear_display(self):
#         if not self._enabled:
#             return
#         image = Image.new('1', (self._width, self._height))
#         self.sensor_device.image(image)
#         self.sensor_device.show()


#     def get_ip_address(self):
#         try:
#             hostname = socket.gethostname()
#             result = os.popen(f"ifconfig eth0").read()
#             IPAddr = result.split("inet ")[1].split()[0]
#             return f'{hostname}@{IPAddr}'
#         except:
#             return "Unknown"
class Display:
    """
    Display showcasing Pi information and status
    """
    def __init__(self):
        self.width = 128
        self.height = 64
        self.font = ImageFont.load_default()
        self.enabled = True  # Initialize as True, will be set to False on error
        self.ip = self.get_ip_address()
        self._i2c = board.I2C()
        try:
            self._disp = adafruit_ssd1306.SSD1306_I2C(self.width,self.height, self._i2c)
            self._disp.width = self.width
            self._disp.height = self.height
            # self.disp.begin()
            self._disp.fill(0)
            # self.disp.clear()
            self._disp.show()
        except RuntimeError as e:
            print(f'Display: {e}', file=sys.stderr)
            self.enabled = False
        # self._batt = Battery()

    def display_time(self):
        if not self.enabled:
            return

        image = Image.new('1', (self.width, self.height))
        draw = ImageDraw.Draw(image)
        
        # Clear the image buffer
        draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        # Get the current time
        current_time = time.strftime('%H:%M:%S')
        
        # Draw the time on the image
        draw.text((0, 1), current_time, font=self.font, fill=255)

        # Display the image
        self._disp.image(image)
        self._disp.show()

    def display_msg(self, status, img_count=1):
        if not self.enabled:
            return

        # msg = [f'{status}', 
        #         time.strftime('%H:%M:%S'),
        #         f'Img count: {img_count}',
        #         f'IP: {self.ip}']
        msg = [f'{status}', 
                time.strftime('%H:%M:%S'),
                f'Img count: {img_count}',]
        
        # logging.info(f"Battery Charge (SOC & Voltage): {self._batt.SoC()}% {self._batt.volt_diff()}%")
        image = Image.new('1', (self.width, self.height))
        draw = ImageDraw.Draw(image)
        
        # Clear the image buffer
        draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        #_, font_height = self.font.getsize('Sample Text')
        x, y = 0, 0
        for item in msg:
            draw.text((x, y), item, font=self.font, fill=255)
            y += 14
        
        self._disp.image(image)
        self._disp.show()
    # def get_batt_charge(self):
    #     return self._batt.SoC(), self._batt.volt_diff()  

    def clear_display(self):
        if not self.enabled:
            return
        image = Image.new('1', (self.width, self.height))
        self._disp.image(image)
        self._disp.show()


    def get_ip_address(self):
        try:
            hostname = socket.gethostname()
            result = os.popen(f"ifconfig eth0").read()
            IPAddr = result.split("inet ")[1].split()[0]
            return f'{hostname}@{IPAddr}'
        except:
            return "Unknown"
    def disp_deinit(self):
        """
        Deinitialize the battery monitor and the display
        """
        # self._batt.sensor_deinit()
        self._i2c.deinit()

# if __name__ == '__main__':
#     disp = Display()
#     ip = disp.get_ip_address()
    

#     try:
#         while True:
#             msg = [f'Imaging status', 
#                    time.strftime('%H:%M:%S'),
#                    f'IP: {ip}']
#             disp.display_msg(msg)
#             current_second_fraction = time.time() % 1
#             sleep_duration = 1 - current_second_fraction
#             time.sleep(sleep_duration)
#     except KeyboardInterrupt:
#         disp.clear_display()

#     finally:
#         disp.clear_display()



class MultiSensor(Sensor):
    """
    Class that holds the various different sensors for acquiring data

    This will reduce the amount of complexity in the control script.

    It also allows for the saving of all sensor data to csv

    
    NEED TO DETERMINE:
    - periodic batching for backup of CSV
    - do backup everytime we get sensor data
    - or do a combo of both methods
    
    NEED TO ADD:
    - need more error handling
    - need to integrate time component..
    - need to also have realtime monitoring...


    """
    def __init__(self,path_sensors):
        """
        Initialize the different sensor classes
        """
        super().__init__()
        self._temp_rh = TempRHSensor()
        time.sleep(0.5)
        self._light = LightSensor()
        time.sleep(0.5)
        # self._disp = Monitor(128,64)
        # time.sleep(0.5)
        with WittyPi() as witty:
            self._shutdown_dt = witty.get_shutdown_datetime() 
        # self.__battery = 
        # Generate a filename based on the current timestamp and store it as a class property
        ### This could be placed in a different place...
        start_time= datetime.now().strftime('%Y%m%d_%H%M%S')
        self.filename = f'{path_sensors}/sensor_data_{start_time}.csv'# all data is written to this CSV...
    def get_shutdown_datetime(self):
        return self._shutdown_dt

    def add_data(self,img_file,date_time):
        """
        Similar to the prior classes this method will
        focus on adding the data to the sensor data dictionary

        However, this method essentially just calls all of the sensor 
        data acquisition methods.
        """
        # check that time is in proper range based on wittyPi set shutdown time
        if self._shutdown_dt >= date_time:
            ## Add the image and time to the dictionary
            #print(date_time)
            time_current_split = str(date_time.strftime("%Y%m%d_%H%M%S"))
            self.data_dict['time'].append(time_current_split)
            self.data_dict["image_filename"].append(img_file)
            ## Add Temperature and Humidity
            d_t, d_rh = self._temp_rh.temp_rh_data()
            ## Add Light Data
            d_lux, d_v, d_ir, d_fs= self._light.light_data()
        else:
            raise ShutdownTime
        ## Get the cuurrent data
        #print("Current Data")
        #self.display() # displays all data using the sensor display method
        #return d_t, d_rh, d_lux, d_v, d_ir, d_fs
    
    def append_to_csv(self):
        """
        Create and or append the sensor data to the csv file

        ADD into the CSVfile the image name as well which is going to require a function input...
        """
        if not os.path.exists(self.filename):
            # create the csv with headers..
            with open(self.filename, 'w') as data_file:
                    csv_writer = DictWriter(data_file, fieldnames =self.data_dict.keys())
                    csv_writer.writeheader() # write the header...
        with open(self.filename, 'a') as data_file:
            try:
                # Try to pass the dictionary into the csv 
                csv_writer = DictWriter(data_file, fieldnames =self.data_dict.keys())
                #print(self.data_dict.values())
                # first got the length of the list...
                len_list = len(list(self.data_dict.values())[0])
                # looping over each time instance:
                for t in range(len_list):
                    row_data = {}
                    for k in self.data_dict.keys():
                        # add data at this time for sensor 'k' to dictionary
                        row_data[k] = self.data_dict[k][t]
                    # write this row...of data for the timestep...
                    # before the next time instance write what we have to csv
                    csv_writer.writerow(row_data) # appends data to the headers
                
                # reset the data_dict
                for k in self.data_dict:
                    self.data_dict[k] = []
                print("CLEAR!")
                # print(self.data_dict)
                #print(self.data_dict)
            ## FIGURE OUT MORE ON RAISING EXCEPTIONS AND STUFF...
            except Exception as e:
                print(f"An error occurred while appending to the CSV file: {e}")
    def sensors_deint(self):
        print("Deinitializing I2C Bus")
        self._temp_rh.sensor_deinit()
        self._light.sensor_deinit()
        # self._disp.sensor_deinit()
        print("Finished Denitializing I2C Bus...Reading for Reboot")
    def monitor_display(self):
        """Display information to the monitor"""
        ip = self._disp.get_ip_address()
        msg = [f'Imaging status', 
                time.strftime('%H:%M:%S'),
                f'IP: {ip}']
        self._disp.display_msg(msg)
        current_second_fraction = time.time() % 1
        sleep_duration = 1 - current_second_fraction
        time.sleep(sleep_duration)

    def clear_display(self):
        if not self._enabled:
            return
        image = Image.new('1', (self._width, self._height))
        self._disp.image(image)
        self._disp.show()

"""
Right now there is a delay in the display since we 
are not running the display and the sensor acquistion in sync

Two options

1. Create two threads... See sensors_threads script for this....
    - What this script does it essentially embeds all the actions we perform for the MultiSensor in there...
    - It is important to note that what needs to happen is first an initialization of the MultiSensor class
    - Then after that we have the two functions...

2. Use multiprocessing

"""

if __name__ == "__main__":
    """
    Testing Procedure for temperature sensor
    """
    print("Working")
    
    sensors = MultiSensor(path_sensors="/home/pi/data/")
    # Start timer
    start_time = time.time()

    try:
        curr_time = start_time
        while True:
            print("In Loop")
            time.sleep(2)
            time_current_split = datetime.now().strftime('%Y%m%d%H%M%S')
            name = 'bob'
            img_name = str(name + '_' + time_current_split + '.jpg')
            sensors.add_data(img_name,time_current_split )
            sensors.monitor_display()
            if (time.time()-curr_time) >= 30:
                curr_time = time.time()
                sensors.append_to_csv()
            
    except KeyboardInterrupt:
        print("Exiting")
        sensors.clear_display()
        sensors.display()
