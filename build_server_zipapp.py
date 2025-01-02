import os
import shutil
import zipapp

from pathlib import Path

if __name__ == "__main__":
    dirs: list[str] = [
        'server_pkg',
        'server_pkg',
        'server_pkg',
        'server_pkg',
        'colors',
        'resp',
        'detection',
        'redis',
        'redis',
        'redis',
        'redis',
        'redis',
        'redis',
        'redis',
        'redis',
        'tokenizer',
        'tokenizer',
        'parser',
        'parser'
    ]

    files: list[str] = [
        os.path.join('server_pkg', 'server.py'),
        os.path.join('server_pkg', 'connections.py'),
        os.path.join('server_pkg', 'exit_params.py'),
        os.path.join('server_pkg', 'logs.py'),
        os.path.join('colors', 'print_colors.py'),
        os.path.join('resp', 'resp_commands.py'),
        os.path.join('detection', 'detection.py'),
        os.path.join('redis', 'redis_command.py'),
        os.path.join('redis', 'redis_echo.py'),
        os.path.join('redis', 'redis_error.py'),
        os.path.join('redis', 'redis_hello.py'),
        os.path.join('redis', 'redis_info.py'),
        os.path.join('redis', 'redis_ping.py'),
        os.path.join('redis', 'redis_record.py'),
        os.path.join('redis', 'redis_records.py'),
        os.path.join('tokenizer', 'resp_token.py'),
        os.path.join('tokenizer', 'resp_tokenizer.py'),
        os.path.join('parser', 'resp_parser.py'),
        os.path.join('parser', 'execute_command.py')
    ]

    try:
        print("Building uredis-server as PYZ application...")
        os.mkdir("server_app")

        for d in set(dirs):
            os.mkdir(os.path.join('server_app', d))
            Path.touch(os.path.join('server_app', d, '__init__.py'))

        i = 0
        for py in files:
            shutil.copy(py, os.path.join("server_app", dirs[i]))
            i += 1

        shutil.copy('server__main__.py', os.path.join('server_app', '__main__.py'))

        zipapp.create_archive("server_app", "uredis-server.pyz")
        shutil.copy("uredis-server.pyz", "services")
        shutil.rmtree("server_app")
        print("Done.")

    except Exception as message:
        print("Error: " + str(message))
