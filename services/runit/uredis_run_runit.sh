#!/bin/sh
# Run ("run") script for uredis service for runit.
# /etc/sv/uredis/run
exec chpst -u uredis python3 /opt/uredis/uredis-server.pyz -z 15000000000 --daemon-safe --no-pid > /dev/null
