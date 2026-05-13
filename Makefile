PYTHON ?= python3
VENV ?= .venv

.PHONY: setup test backtest plots

setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest

backtest:
	$(PYTHON) -m src.run_backtest

plots:
	$(PYTHON) -m src.make_plots
