VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip3
UVICORN = $(VENV)/bin/uvicorn
PYTEST = $(VENV)/bin/pytest

include .env
export

# Need to use python 3.9 for aws lambda
$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

crawl: $(VENV)/bin/activate
	$(PYTHON) crawl_index.py

esgpt: $(VENV)/bin/activate
	$(PYTHON) es_gpt.py

test: $(VENV)/bin/activate
	$(PYTEST) --verbose es_gpt_test.py -s -vv
app: $(VENV)/bin/activate
	$(UVICORN) app:app --reload --port 7002

clean:
	rm -rf __pycache__
	rm -rf $(VENV)
