# Define variables
APP_NAME = your-app-name
PYTHON = python3
PIP = pip3
FLASK = flask

# Define targets
.PHONY: run
run:
	$(FLASK) run

.PHONY: install
install:
	$(PIP) install -r requirements.txt

.PHONY: clean
clean:
	rm -rf __pycache__

.PHONY: lint
lint:
	$(PYTHON) -m flake8 --exclude=__pycache__ .

.PHONY: test
test:
	$(PYTHON) -m unittest discover

.PHONY: build
build:
	docker build -t $(APP_NAME) .

.PHONY: docker-run
docker-run:
	docker run -p 5000:5000 $(APP_NAME)
