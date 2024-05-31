# Control Script Service...
This details how the control script runs in background as a systemd service...


Created Bash Script called start_bee_cam.sh
```
#!/usr/bin/env bash
# Description: Bash Script that will call the python method
python -m bee_cam.scripts.control
```

After this then tested that it worked properly


Then created the service...
- first created the servce file
```
sudo nano /etc/systemd/system/bee_cam_basic.service
```
- after this point we then can work with the general structure seen in this [tutorial](https://www.thedigitalpictureframe.com/ultimate-guide-systemd-autostart-scripts-raspberry-pi/
```
[Unit]
Description=Service file that will start the bee_cam script up
After=network.target datetime_sync.service # after the RTC.service has been completed

[Service]
Type=oneshot
WorkingDirectory=/home/pi/bee_cam_basic/
User=pi
ExecStart=/bin/sleep 10
ExecStart=/usr/bin/python3 /home/pi/bee_cam_basic/control.py
RemainAfterExit=true

[Install]
WantedBy=multi-user.target

```

- now with final completed change the file permission, make sure in right directory
```
sudo chmod 644 bee_cam.service

- then reload the daemon
```
sudo systemctl daemon-reload
```

- enable to start on boot
```
sudo systemctl enable bee_cam.service
```

- should be good to go now...

- TESTING:
    - Shutdown/Reboot the pi, and then turn pi back on. At this point wait for several minutes. 

    - After several minutes then we need to essentially stop this service

    - After stopping the service then let us go back to check on this service and what happened with the data collected

    ```
    sudo systemctl stop bee_cam.service

    ```
    - After stopping the service then do a reload/restart of it if everything is okay
    ```
    sudo systemctl reload bee_cam.service

    ```


- IF THERE IS AN ISSUE THEN DISABLE THE SERVICE
```
sudo systemctl disable bee_cam.service
```






IMPORTANT: When changes have been made to the python file you will need to restart the specific service...
```
sudo systemctl reload name-of-your-service.service
```



################### BASH SCRIPT TESTING METHOD#################



nohup python control.py &


