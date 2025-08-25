#!/sbin/openrc-run
# Run uredis as an OpenRC service.

name="uredis"
pidfile="/run/uredis.pid"
output_log="/dev/null"
error_log="/dev/null"

command="python3"
command_args="/opt/uredis/uredis-server.pyz -z 15000000000 --daemon-safe --no-pid"

command_background=true
command_user="uredis:uredis"

depend() {
    need net
}
