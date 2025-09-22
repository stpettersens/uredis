import os
import sys
import shutil
import zipfile
import hashlib
import platform

def sha256sum(filename: str) -> str:
    with open(filename, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

if __name__ == "__main__":
    # Create release text for a build.
    pkg: str = ''
    if os.path.exists('uredis-server.pyz'):
        import server_pkg.server as release
        with open('version.txt', 'w') as f:
            pkg = release.get_build_version()
            f.write(pkg + '\n\n')
            with open('CHANGELOG', 'r') as log:
                for l in log.readlines():
                    f.write(l)

    # Create the ZIP file for a release.
    with zipfile.ZipFile(f'{pkg}.zip'.lower().replace(' ', '_'), 'w',
    compression=zipfile.ZIP_DEFLATED) as release:
        release.write('README.md')
        release.write('version.txt')
        release.write('MIT-LICENSE')
        release.write('uredis-server.pyz')
        release.write('uredis-client.pyz')

    # Create the SHA256 checksum text files.
    zip_file = f'{pkg}.zip'.lower().replace(' ', '_')
    checksum_file = f'{pkg} sha256.txt'.lower().replace(' ', '_')
    checksum_latest = 'uredis_latest_sha256.txt'
    checksum_script="uredis-setup_sha256.txt"
    with open(checksum_file, 'w') as chksum:
        chksum.write(f"{sha256sum(zip_file)} {zip_file}")

    with open(checksum_latest, 'w') as lchksum:
        lchksum.write(f"{sha256sum(zip_file)} uredis_latest.zip")

    with open(checksum_script, 'w') as schksum:
        schksum.write(f"{sha256sum("uredis-setup.sh")} uredis-setup.sh")

    sys.exit(0)
