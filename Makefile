make: server

deps:
	uv venv
	uv pip install -r requirements.txt

test_deps:
	uv venv
	uv pip install -r requirements.testing.txt

check_client:
	uvx mypy client__main__.py

check_server:
	uvx mypy server__main__.py

build_client:
	uv run python build_server_zipapp.py

build_server:
	uv run python build_client_zipapp.py

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

test: test_parser

docker:
	uv run python build_docker_image.py

clean:
	@echo Cleaning PYZ for server and client...
	uv run python clear_pyz.py
