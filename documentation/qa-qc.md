# QA/QC Procedure
Below is the outlined procedure for when dealing with calibrating the RTC of the indivudal units and testing them to ensure that they are performing properly.

Currently, this process is manual but we will be implementing a fleed managment system in order to communicate with the various deployed nodes.

## Test 1
* WittyPi 4 Mini Manual Shutdown
    - Power on the WittyPi 4 Mini (using USB-C to WittyPi 4 Mini directly), but dont press the button.
    - Wait until wittypi has a flashing white status light. At this point press the button to power on the Pi.
    - Wait 3 minutes for the pi to power on fully. Wait an additional 5 minutes to ensure that the Pi remains on and is recieving stable voltage. 
    - After this elapsed time press the button on the WittyPi again, this should power down the pi in 1-2 minutes.
    - The WittyPi should then return to a sleep mode with the white status light flashing. If this is not the case then log into the pi again and see the troubleshooting section for the WittyPi.

* Desktop to Console mode
    - ensure that the OS is in console mode with boot to login.
    ```
    sudo raspi-config
    ```
    select boot options
    
    select option for console mode with login

* RTC and WittyPi 4 Mini Time Check
    - With the Pi connected to internet, via ethernet or wifi, proceed to login and check the time
    - First check system time
    ```
    sudo hwclock -r
    ```
    - If system time doesnt match current time then run the following

    ```
    sudo systemctl restart systemd-timesyncd
    ```

    - Check system time again to ensure that it is correct. If there is still an issues then there is likely an issue related to boot/config.txt or udev/hwclock-set. See the RTC section regarding those issues.

    ```
    sudo hwclock -r
    ```

    - Check the WittyPi time. 
    ```
    cd wittypi
    ```
    ```
    ./wittypi.sh
    ```

    - If the WittyPi time is registered as invalid then shutdown the pi as the time.init script should fix that issue.
    ```
    sudo shutdown -h now
    ```
    - Start the Pi back up once white status light is flashing, and check WittyPi time. This time should correspond to the system/network time. If there are issues refer to the WittyPi internal documentation as well as the referenced documentation from UUGear.

## Test 2
* Time Check
    - Shutdown the Pi and leave it for 15 minutes with no power connected to the WittyPi.
    - After this time, reconnect power to the WittyPi and ensure that the Pi will to be able to connect to the local network. Proceed to ssh into the Pi and check for system and WittyPi time.
    ```
    sudo hwclock -r
    ``` 
    ```
    cd wittypi
    ./wittypi.sh
    ```
* Control Script Test
    - run the control script
    ```
    cd bee_cam_basic
    python control.py
    ``` 
    - If errors encountered regarding camera:
        - shutdown pi and check cable connections
        - Do Test 2 from the beginning after making any changes

    - If errors encountered regarding I2C:
        - check i2c 
        ```
        sudo i2cdetect -y 1
        ```
        after running this command there should be 3 i2c connections 08, UU, and 3c.
        - shutdown the pi and check the solder joints and stemma connectors. Additional soldering may be needed.
        - Do Test 2 from the beginning after making any changes

    - If No errors after 5 min:
        - interrupt the current process

## Test 3