VENV=.venv
PYTHON=python3

$(VENV):
	$(PYTHON) -m venv $(VENV)

install: $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

clear:
	rm -rf $(VENV)

run: install
	$(VENV)/bin/python main.py

test: install
	$(VENV)/bin/pytest

update:
	$(VENV)/bin/pip freeze > requirements.txt

.PHONY: install clear run test