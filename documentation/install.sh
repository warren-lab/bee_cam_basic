#!/bin/bash

script_dir="$(dirname "$(realpath "$0")")"

# destination paths
home_path="/home/pi"
service_path="/etc/systemd/system"

install_files() {
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

install_file "$SCRIPT_DIR/time_init.sh" "$home_path" 755

install_file "$SCRIPT_DIR/datetime_sync.service" "$service_path" 644
install_file "$SCRIPT_DIR/bee_cam_basic.service" "$service_path" 644

echo "Reloading systemd daemon"
systemctl daemon-reload

datetime_service="datetime_sync.service"
echo "Enabling and starting $datetime_service"
systemctl enable "$datetime_service"
systemctl start "$datetime_service"

beecam_service="bee_cam_basic.service"
echo "Enabling and starting $beecam_service"
systemctl enable "$beecam_service"
systemctl start "$beecam_service"

echo "Installation complete"
