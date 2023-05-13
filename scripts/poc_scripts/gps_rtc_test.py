import time
import board
import busio
import datetime

# Define I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Define GPS module address
gps_address = 0x10  # Replace this with the correct I2C address of your GPS module

# Define RTC registers
RTC_SECONDS = 0x00
# Other RTC register definitions...

# Buffer to read data into (7 bytes for RTC_SECONDS to RTC_YEAR)
rtc_data = bytearray(7)

# Main loop to continuously read RTC time
while True:
    # Specify the register to start reading from
    i2c.writeto(gps_address, bytes([RTC_SECONDS]), stop=False)
    # Read 7 bytes of data starting from RTC_SECONDS
    i2c.readfrom_into(gps_address, rtc_data)

    # Extract and decode RTC data
    # Make sure to adjust the decoding according to your RTC module's datasheet
    second = rtc_data[0] & 0x7F  # Mask off high bit for seconds
    minute = rtc_data[1] & 0x7F
    hour = rtc_data[2] & 0x3F  # 24-hour mode for hours
    day = rtc_data[3] & 0x3F
    month = rtc_data[4] & 0x1F
    year = rtc_data[5] + 2000  # Adjust year offset as necessary

    # Print the RTC time
    print('RTC timestamp: {}/{}/{} {:02}:{:02}:{:02}'.format(
        month,   # month
        day,     # day
        year,    # year
        hour,    # hour
        minute,  # minute
        second)) # second

    # Delay before the next iteration
    time.sleep(1)


# # RTC register addresses
# # These must be defined according to your device's datasheet
# RTC_SECONDS = 0x00
# RTC_MINUTES = 0x01
# RTC_HOURS = 0x02
# RTC_DAY = 0x03
# RTC_MONTH = 0x04
# RTC_YEAR = 0x05

# def set_rtc_time(i2c, address):
#     # Get current system time
#     now = datetime.datetime.now()

#     # Prepare time data in the format expected by the RTC
#     # This example assumes the RTC expects binary values.
#     # Adjust this formatting per your RTC's requirements.
#     seconds = now.second
#     minutes = now.minute
#     hours = now.hour
#     day = now.day
#     month = now.month
#     year = now.year - 2000  # Adjust if your RTC has a different base year

#     # Convert time data to bytes and write to the RTC
#     # Note: You might need to adjust data formatting (e.g., to BCD) based on your RTC's datasheet
#     time_data = bytes([RTC_SECONDS, seconds, minutes, hours, day, month, year])
#     i2c.writeto(address, time_data)

# # Ensure I2C is ready
# while not i2c.try_lock():
#     pass

# try:
#     set_rtc_time(i2c, gps_address)
#     print("RTC time set successfully.")
# finally:
#     i2c.unlock()