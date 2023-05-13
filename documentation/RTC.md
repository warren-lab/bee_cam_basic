# Start Up Time initialization
- follow this tutorial first if havent already...
    - https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi/set-rtc-time
    - DO NOT DISABLE THE timesync service
        - will use the timesync service in below steps..


- Commands that are used to reset the DS3231 RTC...
```
sudo hwclock -r 
```

```
sudo systemctl restart systemd-timesyncd
```

check between date and sudo hwclock -r
```
date
```

- If there is network connection:
    - Issue a reset of the ntp protocol and reset the hwclock
    - then check hwclock and date and that they are equal
    - then address the wittypi time if there is network connection also sync

- If no network connection, assume that the hwclock time is good
    - this will mean that that time should be the same between date and sudo hwclock -r
    - If this is true then write that time to the wittyPi...
        using the method system_to_rtc() from the utilities.sh in wittypi...
- 

## Created a bash time sync script:
- time_init.sh
- make sure it is an executable
```
chmod +x 
```

## Creatd a systemd service
went into /etc/systemd/system/directory
- name of service is called datetime_sync

- first created the servce file
```
sudo nano /etc/systemd/system/datetime_sync.service
```

- after this point we then can work with the general structure seen in this [tutorial](https://www.thedigitalpictureframe.com/ultimate-guide-systemd-autostart-scripts-raspberry-pi/)
    * developed the Unit section
        ```
        [Unit]
        Description=Service that checks for network connection and sets time, and then also checks wittypy rtc time and fixes that. Occurs once on boot up.
        After=multi-user.target

        [Service]
        Type=oneshot
        ExecStart=/bin/sleep 20 # add an additional sleep to allow for other services to execute before this one
        ExecStart=/home/pi/time_init.sh
        RemainAfterExit=true

        [Install]
        WantedBy=multi-user.target
        ```
- now with final completed change the file permission
```
sudo chmod 644 datetime_sync.service
```

- after that reload the daemon
```
sudo systemctl daemon-reload
```
- then enable the service to start at boot
```
sudo systemctl enable datetime_sync.service
```

- should be good to go...look into additional methods for starting services manually etc...







