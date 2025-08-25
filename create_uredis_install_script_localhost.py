import os
import sys
import glob
import socket
import shutil

if __name__ == "__main__":
    _dir: str = "localhost"
    script: str = "uredis-setup.sh"
    instructed_url: str = "https://uredis.stpettersen.xyz"
    homelab_url: str = "https://uredis.homelab.stpettersen.xyz"

    ip_address: str = ''

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Use Quad9 DNS service to get local machine's IP.
        s.connect(("9.9.9.9", 80))
        ip_address = s.getsockname()[0]
    finally:
        s.close()

    try:
        releases = os.path.join(_dir, 'releases')
        services = os.path.join(_dir, 'services')
        os.makedirs(releases, exist_ok=True)
        os.makedirs(services, exist_ok=True)
    except:
        pass

    shutil.copy('logo.txt', _dir)
    shutil.copy('requirements.txt', _dir)
    shutil.copy('Dockerfile', _dir)

    shutil.copy(os.path.join('services', 'freebsd', 'uredis_freebsd'), os.path.join(_dir, 'services'))
    shutil.copy(os.path.join('services', 'openbsd', 'uredis_openbsd'), os.path.join(_dir, 'services'))
    shutil.copy(os.path.join('services', 'systemd', 'uredis_systemd'), os.path.join(_dir, 'services'))
    shutil.copy(os.path.join('services', 'openrc', 'uredis_openrc'), os.path.join(_dir, 'services'))

    for f in glob.glob("*.zip"):
        shutil.copy(f, os.path.join(_dir, 'releases', 'uredis_latest.zip'))

    out: list[str] = []
    with open(script) as f:
        lines = f.readlines()
        for l in lines:
            if l.find(instructed_url) != -1:
                out.append(l.replace(instructed_url, f"http://{ip_address}:8000"))
            elif l.find(homelab_url) != -1:
                out.append(l.replace(homelab_url, f"http://{ip_address}:8000"))
            elif l.find('Dockerfile') != -1:
                out.append(l.replace('Dockerfile', 'Dockerfile.txt'))
            elif l.find('-sSf') != -1:
                out.append(l.replace('-sSf', '-sf'))
            else:
                out.append(l)

    with open(os.path.join(_dir, 'setup'), 'w', newline='\n') as f:
        for o in out:
            f.write(o)

    sys.exit(0)
