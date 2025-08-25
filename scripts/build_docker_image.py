import os
import shutil

def get_python() -> str:
    if shutil.which('python3') is not None:
        return 'python3'

    return 'python'

def build_uredis() -> None:
    python: str = get_python()
    os.system(f"{python} build_server_zipapp.py") # Build the server for the container.
    os.system(f"{python} build_client_zipapp.py") # Build the client for the container.

def build_image() -> None:
    if not os.path.exists('uredis-server.pyz'):
        build_uredis()

    os.system('docker build -t uredis_img .')

if __name__ == "__main__":
    build_image()
