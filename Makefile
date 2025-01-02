PYTHON=$(shell ./detect_py)
make: server client

# For inside venv.
check_client:
	uvx mypy client__main__.py
	@echo

check_server:
	uvx mypy server__main__.py
	@echo

build_client:
	python3 build_server_zipapp.pya
	@echo

build_server:
	python3 build_client_zipapp.py
	@echo

test_parser:
	python3 test_parser.py
	@echo

# For outside venv.
init:
	@echo "Looking for Python interpreter:"
	@echo $(PYTHON)
	@echo

server: init
	$(PYTHON) build_server_zipapp.py
	@echo

client: init
	$(PYTHON) build_client_zipapp.py
	@echo

test: init
	$(PYTHON) test_parser.py
	@echo

run_server: init
	$(PYTHON) server__main__.py

run_client: init
	$(PYTHON) client__main__.py

docker:
	$(PYTHON) build_docker_image.py
	@echo

clean:
	@echo Cleaning PYZ for server and client...
	rm -f *.pyz
