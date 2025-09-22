import os
import sys
import glob
import shutil

if __name__ == "__main__":
    _dir: str = "stpettersen_xyz"
    script: str = "uredis-setup.sh"
    homelab_url: str = "https://uredis.homelab.stpettersen.xyz"
    sh_hl_url: str = "https://sh.homelab.stpettersen.xyz"

    try:
        releases = os.path.join(_dir, 'releases')
        services = os.path.join(_dir, 'services')
        os.makedirs(releases, exist_ok=True)
        os.makedirs(services, exist_ok=True)
    except:
        pass

    shutil.copy('logo.txt', _dir)
    shutil.copy('requirements.txt', _dir)
    shutil.copy('Dockerfile', os.path.join(_dir, 'Dockerfile.txt'))
    shutil.copy('MIT-LICENSE', os.path.join(_dir, 'MIT-LICENSE.txt'))

    shutil.copy(os.path.join('services', 'freebsd', 'uredis_freebsd.sh'), os.path.join(_dir, 'services'))
    shutil.copy(os.path.join('services', 'openbsd', 'uredis_openbsd.sh'), os.path.join(_dir, 'services'))
    shutil.copy(os.path.join('services', 'systemd', 'uredis_systemd.sh'), os.path.join(_dir, 'services'))
    shutil.copy(os.path.join('services', 'openrc', 'uredis_openrc.sh'), os.path.join(_dir, 'services'))
    shutil.copy(os.path.join('services', 'runit', 'uredis_run_runit.sh'), os.path.join(_dir, 'services'))
    shutil.copy(os.path.join('services', 's6', 'uredis_run_s6.sh'), os.path.join(_dir, 'services'))

    for f in glob.glob("*.zip"):
        shutil.copy(f, os.path.join(_dir, 'releases', 'uredis_latest.zip'))

    for f in glob.glob("*_sha256.txt"):
        shutil.copy(f, _dir)

    out: list[str] = []
    with open(script) as f:
        lines = f.readlines()
        for l in lines:
            if l.find(homelab_url) != -1:
                out.append(l.replace(homelab_url, "https://uredis.stpettersen.xyz"))
            elif l.find(sh_hl_url) != -1:
                out.append(l.replace(sh_hl_url, "https://sh.stpettersen.xyz"))
            else:
                out.append(l)

    with open(os.path.join(_dir, 'uredis-setup.sh'), 'w', newline='\n') as f:
        for o in out:
            f.write(o)

    sys.exit(0)
