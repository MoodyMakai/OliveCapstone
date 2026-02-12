.PHONY: all install run test clean check lint activate

VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
QUART = $(VENV)/bin/quart
RUFF = $(VENV)/bin/ruff

all: run

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

install: $(VENV)/bin/activate requirements.txt
	$(PIP) install -r requirements.txt
	touch $(VENV)/bin/activate

run:
	$(QUART) run

test:
	$(PYTHON) -m pytest

check:
	$(RUFF) check .

lint:
	$(RUFF) format .

clean:
	rm -rf $(VENV)
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
