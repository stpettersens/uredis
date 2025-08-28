#!/usr/bin/sh
# This script should be invoked ONCE by the corresponding runit service.
python3 /opt/uredis/uredis-server.pyz -z 15000000000 --daemon-safe --no-pid > /dev/null 2>&1
