#! /bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if [ ! -f "start_ripe.sh" ]; then
    echo "You have to execute this command from the base folder"
    echo "Aborting."
    exit 1
fi

pip3 install -r requirements.txt

cat <<EOT >> /lib/systemd/system/ripe.service
[Unit]
Description=Ripe Service
After=multi-user.target

[Service]
Type=idle
ExecStart=$PWD/start_ripe.sh

[Install]
WantedBy=multi-user.target
EOT