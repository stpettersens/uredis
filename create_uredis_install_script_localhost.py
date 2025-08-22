import os
import sys
import glob
import shutil

if __name__ == "__main__":
    _dir: str = "localhost"
    script: str = "uredis-setup.sh"
    url: str = "https://uredis.homelab.stpettersen.xyz"

    try:
        os.mkdir(_dir)
        os.mkdir(os.path.join(_dir, 'releases'))
    except:
        pass

    shutil.copy('logo.txt', _dir)
    shutil.copy('requirements.txt', _dir)
    shutil.copy('Dockerfile', os.path.join(_dir, 'Dockerfile.txt'))

    for f in glob.glob("*.zip"):
        shutil.copy(f, os.path.join(_dir, 'releases', 'uredis_latest.zip'))

    out: list[str] = []
    with open(script) as f:
        lines = f.readlines()
        for l in lines:
            if l.find(url) != -1:
                out.append(l.replace(url, "http://localhost:8000"))
            elif l.find('Dockerfile') != -1:
                out.append(l.replace('Dockerfile', 'Dockerfile.txt'))
            else:
                out.append(l)

    with open(os.path.join(_dir, 'setup.txt'), 'w') as f:
        for o in out:
            f.write(o)

    sys.exit(0)
