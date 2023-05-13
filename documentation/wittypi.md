# WittyPi Documentation/Notes

## BeforeShutdown 
- Add the following the the beforeshutdown bash script int he wittypi directory

```
if who | grep -q 'pts/'; then
    echo "Active SSH connections found. Proceeding with shutdown."
    sudo pkill -SIGTERM sshd
    sleep 5
    # Place your shutdown or script commands here
else
    echo "No active SSH connections. Skipping certain shutdown procedures."
    # Optionally skip shutdown or run alternative commands
fi
```


## Start/Stop Systemd Service
- This was slightly changed as the kill -9 method was used which is an abrupt termination of a process instead of gradual termination
which occurs with SIGTERM or kill -15. Based on this a new method was developed which is outlined below...


In order to access the service...

- Needed to determin the path to the service. The below command does this.
```
systemctl cat wittypi.service
```
- Navigated to this file:
```
sudo nano /etc/init.d/wittypi
```

- Then once in the wittypi systemd service file added additional functionality in order to address concerns related to forceful termination
Original
```
#!/bin/bash
# /etc/init.d/wittypi
### BEGIN INIT INFO
# Provides: wittypi
# Required-Start: $remote_fs $syslog
# Required-Stop: $remote_fs $syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Witty Pi 4 initialize script
# Description: This service is used to manage Witty Pi 4 service
### END INIT INFO
case "$1" in

start)
echo "Starting Witty Pi 4 Daemon..."
/home/pi/wittypi/daemon.sh &
sleep 1
daemonPid=$(ps --ppid $! -o pid=)
echo $daemonPid > /var/run/wittypi_daemon.pid
;;
stop)
echo "Stopping Witty Pi 4 Daemon..."
daemonPid=$(cat /var/run/wittypi_daemon.pid)
kill -9 $daemonPid
;;
*)
echo "Usage: /etc/init.d/wittypi start|stop"
exit 1
;;
esac
exit 0
```

New Version:
```
#!/bin/bash
# /etc/init.d/wittypi
### BEGIN INIT INFO
# Provides: wittypi
# Required-Start: $remote_fs $syslog
# Required-Stop: $remote_fs $syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Witty Pi 4 initialize script
# Description: This service is used to manage Witty Pi 4 service
### END INIT INFO
case "$1" in
start)
echo "Starting Witty Pi 4 Daemon..."
/home/pi/wittypi/daemon.sh &
sleep 1
daemonPid=$(ps --ppid $! -o pid=)
echo $daemonPid > /var/run/wittypi_daemon.pid
;;
stop)
echo "Stopping Witty Pi 4 Daemon..."
# first got the PID of the daemon
daemonPid=$(cat /var/run/wittypi_daemon.pid)
if [ -n "$daemonPid" ]; then
kill -15 $daemonPid # send SIGTERM signal to daemom using PID
sleep 10 # sleep for 10 seconds to allow all processes to terminate
# Check if the processes are still running
if kill -0 $daemonPid 2>/dev/null; then
echo "Daemon did not terminate, forcing shutdown..."
kill -9 $daemonPid # force termination if not graceful shutdown
else
echo "Daemon terminated gracefully"
fi
else
echo "Daemon PID not found"
fi
;;
*)
echo "Usage: /etc/init.d/wittypi start|stop"
exit 1
;;
esac
exit 0 
```

## Button On/Off
- In order to utilize