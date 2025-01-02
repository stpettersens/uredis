import os
import shutil
import zipapp

from pathlib import Path

if __name__ == "__main__":
    dirs: list[str] = [
        'client_pkg',
        'colors',
        'resp',
        'resp',
        'resp',
        'resp',
        'detection'
    ]

    files: list[str] = [
        os.path.join('client_pkg', 'client.py'),
        os.path.join('colors', 'print_colors.py'),
        os.path.join('resp', 'resp_type.py'),
        os.path.join('resp', 'resp_encoder.py'),
        os.path.join('resp', 'resp_decoder.py'),
        os.path.join('resp', 'resp_commands.py'),
        os.path.join('detection', 'detection.py')
    ]

    try:
        print("Building uredis-client as PYZ application...")
        os.mkdir("client_app")

        for d in set(dirs):
            os.mkdir(os.path.join('client_app', d))
            Path.touch(os.path.join('client_app', d, '__init__.py'))

        i = 0
        for py in files:
            shutil.copy(py, os.path.join("client_app", dirs[i]))
            i += 1

        shutil.copy('client__main__.py', os.path.join('client_app', '__main__.py'))

        zipapp.create_archive("client_app", "uredis-client.pyz")
        shutil.copy("uredis-client.pyz", "services")
        shutil.rmtree("client_app")
        print("Done.")

    except Exception as message:
        print("Error: " + str(message))
