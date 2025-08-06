import os
import sys
import zipfile

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
        release.write('uredis-server.pyz')
        release.write('uredis-client.pyz')

    sys.exit(0)
