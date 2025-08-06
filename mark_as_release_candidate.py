import os
import sys
import zipfile

if __name__ == "__main__":
    # Mark a build as release candidate rather than final version.
    apps: list[str] = [
        'uredis-server.pyz',
        'uredis-client.pyz'
    ]

    for app in apps:
        i: int = 0
        if os.path.exists(app):
            with zipfile.ZipFile(app, 'a') as zipped:
                zipped.writestr('.rc', '')
        else:
            print("Run make build_client and make build_server first.")
            sys.exit(-1)

        i += 1

    sys.exit(0)
