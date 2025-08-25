#!/bin/ksh
#
# For OpenBSD: Run uredis-server as a daemon.
# This daemon will currently time out, but it does actually work :)

daemon="/usr/local/bin/python3 /usr/local/opt/uredis/uredis-server.pyz --dir /usr/local/opt/uredis/ -z 15000000000 --daemon-safe"

. /etc/rc.d/rc.subr

rc_stop="pkill -SIGTERM -P $(cat /usr/local/opt/uredis/uredis.pid) && sleep 3"

rc_cmd $1
