import smbus

def scan_i2c(bus_number):
    bus = smbus.SMBus(bus_number)
    devices = []
    for address in range(0, 128):
        try:
            bus.read_byte(address)
            devices.append(hex(address))
        except IOError:
            pass
    return devices

# Scan I2C bus 1
print("Scanning I2C bus 1:")
devices_on_bus1 = scan_i2c(1)
if devices_on_bus1:
    print("Devices found:", ", ".join(devices_on_bus1))
else:
    print("No devices found on bus 1.")

# Scan I2C bus 2
print("\nScanning I2C bus 2:")
devices_on_bus2 = scan_i2c(2)
if devices_on_bus2:
    print("Devices found:", ", ".join(devices_on_bus2))
else:
    print("No devices found on bus 2.")