[Unit]
Description=uredis-server service
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=10
User=uredis
ExecStart=python3 /opt/uredis/uredis-server.pyz -z 15000000000 --daemon-safe --no-pid

[Install]
WantedBy=multi-user.target
