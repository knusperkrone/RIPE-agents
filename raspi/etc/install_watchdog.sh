#! /bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if [ ! -f "watchdog.py" ]; then
    echo "You have to execute this command from the base folder"
    echo "Aborting."
    exit 1
fi

set -o errexit
apt install git
pip3 install -r requirements.txt

cat <<EOT > /lib/systemd/system/ripe.service
[Unit]
Description=Ripe Service
After=multi-user.target

[Service]
Restart=always
WorkingDirectory=$PWD
ExecStart=python3 -u ./watchdog.py
EnvironmentFile=$PWD/.env

[Install]
WantedBy=multi-user.target
EOT

systemctl start ripe.service
systemctl enable ripe.service
