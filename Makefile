.PHONY: install dev test lint run demo

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v --tb=short

lint:
	ruff check src/ tests/

run:
	streamlit run src/viz/app.py

demo:
	python examples/demo.py
