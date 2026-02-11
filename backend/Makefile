.PHONY: all help install venv run test clean

VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

install: $(VENV)/bin/activate
	$(PIP) install -r requirements.txt

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	touch $(VENV)/bin/activate

run: $(VENV)/bin/activate
	flask --app app run

test: $(VENV)/bin/activate
	$(PYTHON) -m pytest

clean:
	rm -rf $(VENV)
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
