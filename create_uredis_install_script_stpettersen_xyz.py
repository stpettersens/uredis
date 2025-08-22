import os
import sys
import glob
import shutil

if __name__ == "__main__":
    _dir: str = "stpettersen_xyz"
    script: str = "uredis-setup.sh"
    url: str = "https://uredis.homelab.stpettersen.xyz"

    try:
        os.mkdir(_dir)
        os.mkdir(os.path.join(_dir, 'releases'))
    except:
        pass

    shutil.copy('logo.txt', _dir)
    shutil.copy('requirements.txt', _dir)
    shutil.copy('Dockerfile', _dir)

    for f in glob.glob("*.zip"):
        shutil.copy(f, os.path.join(_dir, 'releases', 'uredis_latest.zip'))

    out: list[str] = []
    with open(script) as f:
        lines = f.readlines()
        for l in lines:
            if l.find(url) != -1:
                out.append(l.replace(url, "https://uredis.stpettersen.xyz"))
            else:
                out.append(l)

    with open(os.path.join(_dir, 'setup'), 'w') as f:
        for o in out:
            f.write(o)

    sys.exit(0)
