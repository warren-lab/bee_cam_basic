#!/bin/bash


install_apt_packages() {
  local packages=("$@")
  echo "Updating package list..."
  sudo apt-get update -y
  sudo apt-get upgrade -y
  echo "Installing apt packages: ${packages[*]}"
  sudo apt-get install -y "${packages[@]}"
}

install_pip_packages() {
  local packages=("$@")
  echo "Installing pip..."
  sudo apt-get install -y python3-pip
  echo "Installing pip packages: ${packages[*]}"
  pip3 install "${packages[@]}"
}

APT_PACKAGES=(
  python3-picamera2
  feh
)

PIP_PACKAGES=(
  adafruit-blinka
  adafruit-circuitpython-si7021
  adafruit-circuitpython-tsl2591
  adafruit-circuitpython-ssd1306
  smbus2
  psutil
)

install_apt_packages "${APT_PACKAGES[@]}"

install_pip_packages "${PIP_PACKAGES[@]}"

pip3 uninstall --yes "numpy"
pip3 install "numpy"

sudo apt-get -y remove fake-hwclock
sudo update-rc.d -f fake-hwclock remove
sudo systemctl disable fake-hwclock

sudo rm -f /lib/udev/hwclock-set

script_dir="$(dirname "$(realpath "$0")")"

# destination paths
home_path="/home/pi"
service_path="/etc/systemd/system"

install_file() {
  local src_file=$1
  local dest_dir=$2
  local file_permission=$3
  local dest_file="$dest_dir/$(basename "$src_file")"

  if [ -f "$dest_file" ]; then
    echo "File $dest_file already exists, skipping."
  else
    if [ -f "$src_file" ]; then
      echo "Copying $(basename "$src_file") to $dest_dir"
      cp "$src_file" "$dest_dir"
      chmod "$file_permission" "$dest_file"
    else
      echo "Source file $src_file does not exist, skipping."
    fi
  fi
}

install_file "$script_dir/time_init.sh" "$home_path" 755
install_file "$script_dir/hwclock-set" "/lib/udev/hwclock-set" 755

install_file "$script_dir/datetime_sync.service" "$service_path" 644
install_file "$script_dir/bee_cam_basic.service" "$service_path" 644

install_file "$script_dir/config.ini.example" "$home_path/bee_cam_basic/config.ini" 644
chown "pi:pi" "/home/pi/bee_cam_basic/config.ini"

echo "Reloading systemd daemon"
systemctl daemon-reload

datetime_service="datetime_sync.service"
echo "Enabling and starting $datetime_service"
systemctl enable "$datetime_service"

beecam_service="bee_cam_basic.service"
echo "Enabling and starting $beecam_service"
systemctl enable "$beecam_service"

cd /home/pi

echo "Downloading and running WittyPi4 install script"
wget https://www.uugear.com/repo/WittyPi4/install.sh -O /home/pi/wittypi_install.sh
sudo sh /home/pi/wittypi_install.sh
rm /home/pi/wittypi_install.sh

DHCPCD_CONF="/etc/dhcpcd.conf"
STATIC_IP_CONFIG="
interface eth0
static ip_address=10.42.0.106/24
static routers=10.42.0.1
static domain_name_servers=8.8.8.8 8.8.4.4
"

if ! grep -q "static ip_address=10.42.0.106/24" "$DHCPCD_CONF"; then
  echo "Adding static IP configuration to $DHCPCD_CONF"
  sudo bash -c "echo '$STATIC_IP_CONFIG' >> $DHCPCD_CONF"
else
  echo "Static IP configuration already exists in $DHCPCD_CONF, skipping."
fi

BOOT_CONFIG="/boot/config.txt"
BOOT_CONFIG_ENTRIES="
dtoverlay=i2c-rtc,ds3231
camera_auto_detect=1
"

for entry in $BOOT_CONFIG_ENTRIES; do
  if ! grep -q "^$entry" "$BOOT_CONFIG"; then
    echo "Adding $entry to $BOOT_CONFIG"
    sudo bash -c "echo '$entry' >> $BOOT_CONFIG"
  else
    echo "$entry already exists in $BOOT_CONFIG, skipping."
  fi
done

# Add to PATH in .bashrc
BASHRC="/home/pi/.bashrc"
PATH_ENTRY="export PATH=\$PATH:/home/pi/.local/bin"

if ! grep -q "^$PATH_ENTRY" "$BASHRC"; then
  echo "Adding $PATH_ENTRY to $BASHRC"
  echo "$PATH_ENTRY" >> "$BASHRC"
else
  echo "$PATH_ENTRY already exists in $BASHRC, skipping."
fi

source /home/pi/.bashrc

if [ ! -d "/home/pi/data" ]; then
  echo "Creating /home/pi/data directory"
  sudo mkdir -p /home/pi/data
  sudo chown pi:pi /home/pi/data
else
  echo "/home/pi/data directory already exists, skipping."
fi


echo "Installation complete"
