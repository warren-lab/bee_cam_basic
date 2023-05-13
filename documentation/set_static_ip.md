# Setting Static IP Address

1. Get the current IP address, router gateway and the router DNS IP
    - Current IP (look under eth0)
    ```
    hostname -I
    ``` 
    
    - router gateway
    ```
    ip r | grep default
    ```

    - router DNS IP
    ```
    sudo nano /etc/resolv.conf
    ```
2. Now go to the dhcpcd.conf file to configure static IP settings
    - (For each Pi make sure that the IP settings relate to the Pi Number in someway) Fill in the x values with appropriate values
    ```
    interface eth0
    static ip_address=xx.xx.xx.xx/24
    static routers=xx.xx.x.x
    static domain_name_servers=xx.xx.x.x
    ```

```

```