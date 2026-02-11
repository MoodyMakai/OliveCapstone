.PHONY: all install run test clean

VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
FLASK = $(VENV)/bin/flask

all: run

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

install: $(VENV)/bin/activate requirements.txt
	$(PIP) install -r requirements.txt
	touch $(VENV)/bin/activate

run: install
	$(FLASK) --app app run

test: install
	$(PYTHON) -m pytest

clean:
	rm -rf $(VENV)
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete