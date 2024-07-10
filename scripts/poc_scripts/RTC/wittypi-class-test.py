from smbus2 import SMBus
from datetime import datetime,timedelta
import time
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
        sets the shutdown to occur at 7pm (TEST CASE 9:30 pm)

        The actual shutdown executed by the shutdown script will happen at 9:35pm to give a bit more buffer
        """
        curr_time = self.get_current_time()
        # Set the shutdown time for today (will be 7pm normally but 9:30pm if testing!)
        self._shutdown_datetime= curr_time.replace(hour = 21,minute = 20, second = 0)# amount of time until shutdown (at least 3 minutes)
        print(self._shutdown_datetime)
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
        shutdown_datetime = self.get_shutdown_datetime() 
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
        
        In this case it sets the start up time to be 7am or 9:45pm 
        """
        # SET STARTUP!
        ## get the current time
        start_time = self.get_current_time() 
        ## get the time for the next day, as the experiment will start on button click initally but we want to assign every single next boot...
        start_time = start_time 
        ## now for the start time need to reassign the actual hour,min,second for the experimental start
        start_time =  start_time.replace(hour=22,minute=35,second=0)
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
if __name__ == "__main__":
    with WittyPi() as witty:
        shutdown_datetime = witty.get_shutdown_datetime()
        witty.shutdown()
        witty.startup()