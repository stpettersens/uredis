#!/usr/bin/env bash
# This script should be invoked by the corresponding runit service.

# Ensure uredis-server application is only run once.
LOCKFILE="/opt/uredis/uredis.lock"
exec 200>"$LOCKFILE"
flock -n 200 || { echo "Another uredis-server instance is running"; exit 1; }
echo $$ 1>&200

# This is still being run more than once! wth!
python3 /opt/uredis/uredis-server.pyz -z 15000000000 --daemon-safe --no-pid > /dev/null 2>&1
