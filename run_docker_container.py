import os
import sys
import json
import subprocess

def run_docker_container(app_name: str = 'default') -> None:
    # Create network for the given %app_name%_network.
    os.system(f'docker network {app_name}_network')

    # Run a container uredis_%app_name% using the uredis_img image.
    os.system(f'docker run --network {app_name}_network -n uredis_{app_name} -h uredis -v {os.getcwd()}:/opt/uredis -d uredis_img')

def create_env_file_for_app(app_name: str = 'default') -> None:
    # First get the IP of the uredis_%app_name%.
    response = subprocess.run([
        'docker',
        'inspect',
        '--format',
        '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
        f'uredis_{app_name}'
    ],
    capture_output=True,
    text=True)

    returned_json: dict = json.loads(result.stdout)

    # Then write it out to a .env file one level above 'uredis' subdirectory.
    # for the target application which uses uredis.
    target_app_dir: str = os.path.join(os.path.dirname(__file__), os.pardir)
    with open(os.path.join(target_app_dir, '.env', 'w') as f:
        f.write(f'APP_NETWORK={app_name}_network\n')
        f.write(f'{app_name.upper()}_REDIS_HOST=TODO\n')
        f.write(f'{app_name.upper()}_REDIS_PORT=6379\n')

if __name__ == "__main__":
    if len(sys.argv) == 3:
        run_docker_container(sys.argv[1])
        create_env_file_for_app(sys.argv[1])
    else:
        run_docker_container()
        create_env_file_for_app()
