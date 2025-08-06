import os
import shutil

def get_python() -> str:
    if shutil.which('python3') is not None:
        return 'python3'

    if shutil.which('pypy3') is not None:
        return 'pypy3'

    if shutil.which('pypy') is not None:
        return 'pypy'

    return 'python'

def get_build_uredis() -> None:
    python: str = get_python()
    os.system(f"{python} build_server_zipapp.py") # Build the server for the container.
    os.system(f"{python} build_client_zipapp.py") # Build the client for the container.
    #shutil.copy('services/uredis-client', 'uredis-client') # Copy shell wrapper for client.

def build_image() -> None:
    if not os.path.exists('uredis-server.pyz'):
        get_build_uredis()

    os.system('docker build -t uredis_img .')
    #os.remove('uredis-client')

if __name__ == "__main__":
    build_image()
