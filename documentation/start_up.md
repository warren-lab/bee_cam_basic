# Start Up Notes for Bee_Cam

## Powering up Bee_Cam Device:
1. Connect LiPo Battery (that has a battery state more than 20%). Or low power LiPo Battery in addition to 5v Usb-C battery

2. Connect Solar Power via DC-Connection
 - ???Determine if Usb-c battery needs to be removed or if all three sources can be utilized at same time.???

3. Power the Pi
- Once power has been plugged in and WittyPi Mini White Light is flashing then press the WittyPi Button to send power to the Pi.

## Lab Connection to Bee_Cam
1. Ensure proper connection to Wired Connection in Ubuntu Networking Settings
2. Configure the ssh config file
- See the documentation on networking in lab wiki for how to do this.
3. Connect to the Pi
* Use the ssh command:
```
ssh bee_cam
```
* Note: that it will take a minute after connecting power for the ssh connection to be established so be patient if you get errors related to "port 22: No route to host".
* If wanting to access files from the Pi do an sshfs. This enables use of code editor from Ubuntu machine.
```
sshfs pi@[hostname]: ~/pi_mount
```

4. Shutting down 
* Shutdown the pi from within the ssh connection
```
sudo shutdown -h now
```

5. Remove Power

## Field Connection to Bee_Cam