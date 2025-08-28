#!/usr/bin/sh
# This script should be invoked by the corresponding runit service.
# Flock prevents the server running multiple times.
flock -n /opt/uredis/uredis.lock --command /usr/local/bin/uredis-service.sh
