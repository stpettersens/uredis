#!/bin/sh

# PROVIDE: uredis
# REQUIRE: DAEMON cleanvar frotz netif
# BEFORE:  LOGIN
# KEYWORD: nojail shutdown

. /etc/rc.subr

name="uredis"
desc="Run uredis-server as a daemon."
rcvar="uredis_enable"
start_cmd="uredis_start"
stop_cmd="uredis_stop"

uredis_start()
{
	echo "Starting uredis-server as a daemon."
	/usr/sbin/daemon -u uredis /usr/local/bin/python3 /usr/local/opt/uredis/uredis-server.pyz -z 15000000000 --daemon-safe > /dev/null
}

uredis_stop()
{
	echo "Stopping uredis-server daemon."
	pkill -SIGTERM -P $(cat /usr/local/opt/uredis/uredis.pid)
	sleep 3
}

load_rc_config "$name"
run_rc_command "$1"
