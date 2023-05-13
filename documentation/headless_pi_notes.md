1. Flash new OS with Field_Trap folder

2. Enabling ssh on Pi:

    - First execute:
        ```
        sudo raspi-config
        ```

    - Then go to Interface Options and Enable ssh
<br>

3. Install feh on the Pi
    - this is a lightweight image viewer and cataloguer

        ```
        sudo apt-get install feh
        ```
<br>

4. Before continuing on your linux machine determine the hostname of your Pi device by running the following in the terminal command
    ```
    hostname -I
    ```
    
5. From your linux machine:
    ```
    ssh-keygen -R [hostname]
    ```
    ```
    ssh -X [hostname]
    ```
    - Then run ./preview.sh will to test the image output
    ```
    run ./preview.sh 
    ```

6. Now go back to the Pi device to set up run on boot!

    ```
    sudo nano /etc/rc.local
    ```
    - Within the rc.local file add the following lines:
    ```
    sleep 5
    sudo python /[location_of_script] -[script_arg] &
    ```

7. Make sure control.json is set to correct params

8. If booted to CLI, start desktop with:
    ```
    startx
    ```

For Working on the Pi on Desktop through Vscode:
1. First initialize the sshfs to mount a remote file system to the local system.
    ```
    sshfs pi@[ip address]: ~/[directory]
    ```
    - This is a directory where you want to mount the pi and once we go to this directory all files on the pi will be present.
2. After initializing and starting the sshfs then ssh into the pi in order to run the scripts on the pi through the terminal.
    ```
    ssh pi@[ip_address]
    ```

Running the script for testing:
- from outside of the directory containing the repo
```
python -m beecam.scripts.image2.py 
```


