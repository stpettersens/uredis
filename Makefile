uname := $(shell uname)
bash=bash

ifeq ($(uname),Windows)
	bash=@echo
endif

make: server

all: build_server build_client

deps:
	uv venv
	uv pip install -r requirements.txt

check_client:
	uvx mypy client__main__.py

check_server:
	uvx mypy server__main__.py

build_client:
	uv run python scripts/build_client_zipapp.py

build_server:
	uv run python scripts/build_server_zipapp.py

rc:
	uv run python scripts/mark_as_release_candidate.py

test_parser:
	uv run python test_parser.py

server:
	uv run python server__main__.py

client:
	uv run python client__main__.py

built_server:
	uv run python uredis-server.pyz

built_client:
	uv run python uredis-client.pyz

package:
	uv run python create_release_pkg.py

test: test_parser

build_docker:
	uv run python scripts/build_docker_image.py

run_docker:
	uv run python scripts/run_docker_container.py

update: package
	@echo
	$(bash) -n uredis-setup.sh
	@echo
	@copyparty_sync

webserver: package
	uv run python create_uredis_install_script_localhost.py
	cd localhost && uv run python -m http.server

deploy: package
	uv run python create_uredis_install_script_stpettersen_xyz.py

clean:
	@echo Cleaning PYZs and ZIPs for server and client...
	uv run python scripts/clear_pyz.py
