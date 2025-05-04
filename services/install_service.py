import os
import sys
import shutil
import platform
import subprocess

targets = [
    "exit (don't install anything).",
    "systemd",
    "freebsd",
    "openbsd",
    "windows"
]

def list_services():
    print('Run this as doas/sudo on Unix-likes.')
    print('uredis-server is available as a service for: ')
    print()
    for i, t in enumerate(targets):
        print('{}) {}'.format(i, t))

    print()
    print('Enter an option to install the service for: ')
    sys.exit(install_service(int(input())))

def install_service(number: int) -> int:
    if not os.path.exists('uredis-server.pyz'):
        print('Please build uredis-server as PYZ first!')
        return -1

    if number < 0 or number >= len(targets):
        print("Invalid option")
        return -1

    elif number == 1:
        if platform.system() != 'Linux':
            print("Not on Linux!")
            return -1

        os.system('useradd -m uredis')
        os.system('mkdir -p /opt/uredis')
        shutil.copy('uredis-server.pyz', '/opt/uredis/uredis-server.pyz')
        shutil.copy('uredis-client.pyz', '/opt/uredis/uredis-client.pyz')
        shutil.copy('systemd/uredis_systemd.service', '/etc/systemd/system/uredis.service')
        shutil.copy('uredis-server', '/usr/bin/uredis-server')
        shutil.copy('uredis-client', '/usr/bin/uredis-client')
        os.system('chmod +x /usr/bin/uredis-server')
        os.system('chmod +x /usr/bin/uredis-client')
        os.system('chown -R uredis:uredis /opt/uredis')
        os.system('systemctl enable uredis')
        os.system('systemctl start uredis')
        os.system('systemctl daemon-reload')

    elif number == 2:
         if platform.system() != 'FreeBSD':
             print("Not on FreeBSD!")
             return -1

         os.system('pw useradd uredis')
         os.system('mkdir -p /opt/uredis')
         shutil.copy('uredis-server.pyz', '/opt/uredis/uredis-server.pyz')
         shutil.copy('uredis-client.pyz', '/opt/uredis/uredis-client.pyz')
         shutil.copy('freebsd/uredis_freebsd', '/etc/rc.d/uredis')
         shutil.copy('uredis-server', '/usr/local/bin/uredis-server')
         shutil.copy('uredis-client', '/usr/local/bin/uredis-client')
         os.system('chmod +x /usr/local/bin/uredis-server')
         os.system('chmod +x /usr/local/bin/uredis-client')
         os.system('chown -R uredis:uredis /opt/uredis')
         os.system('chmod +x /etc/rc.d/uredis')
         os.system('service uredis onestart')
         os.system('service uredis enable')

    elif number == 3:
        if platform.system() != 'OpenBSD':
            print("Not on OpenBSD!")
            return -1

        os.system('useradd uredis')
        os.system('mkdir -p /opt/uredis')
        shutil.copy('uredis-server.pyz', '/opt/uredis/uredis-server.pyz')
        shutil.copy('openbsd/uredis_openbsd', '/etc/rc.d/uredis')
        shutil.copy('uredis-server', '/usr/local/bin/uredis-server')
        shutil.copy('uredis-client', '/usr/local/bin/uredis-client')
        os.system('chmod +x /usr/local/bin/uredis-server')
        os.system('chmod +x /usr/local/bin/uredis-client')
        os.system('chmod +x /etc/rc.d/uredis')
        os.system('touch /opt/uredis/uredis.pid')
        os.system('chown -R uredis:uredis /opt/uredis')
        os.system('rcctl set uredis user uredis')
        os.system('rcctl start uredis')
        os.system('rcctl enable uredis')

    elif number == 4:
        if platform().system() != 'Windows':
            print("Not on Windows!")
            return -1

        # !TODO

        os.system('InstallUtil.exe windows/uredis-service.exe')
        print('ATTENTION: Enable the "uredis-service" service in Services Manager (services.msc)...')
        subprocess.call('services.msc', shell=True)

    return 0

if __name__ == "__main__":
    list_services()
