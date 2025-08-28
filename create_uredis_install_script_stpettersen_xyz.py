import os
import sys
import glob
import shutil

if __name__ == "__main__":
    _dir: str = "stpettersen_xyz"
    script: str = "uredis-setup.sh"
    homelab_url: str = "https://uredis.homelab.stpettersen.xyz"

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
    shutil.copy(os.path.join('services', 'runit', 'uredis_run_runit'), os.path.join(_dir, 'services'))
    shutil.copy(os.path.join('services', 'runit', 'uredis-flock_runit.sh'), os.path.join(_dir, 'services'))
    shutil.copy(os.path.join('services', 'runit', 'uredis-service_runit.sh'), os.path.join(_dir, 'services'))

    for f in glob.glob("*.zip"):
        shutil.copy(f, os.path.join(_dir, 'releases', 'uredis_latest.zip'))

    out: list[str] = []
    with open(script) as f:
        lines = f.readlines()
        for l in lines:
            if l.find(homelab_url) != -1:
                out.append(l.replace(homelab_url, "https://uredis.stpettersen.xyz"))
            else:
                out.append(l)

    with open(os.path.join(_dir, 'setup'), 'w', newline='\n') as f:
        for o in out:
            f.write(o)

    sys.exit(0)
