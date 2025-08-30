#!/bin/execlineb -P
# Run uredis as an S6 service.
s6-setuidgid uredis
exec python3 /opt/uredis/uredis-server.pyz -z 15000000000 --daemon-safe --no-pid > /dev/null
