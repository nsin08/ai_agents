.PHONY: run test lint

run:
	uv run python labs/00/src/hello_agent.py

test:
	uv run pytest labs/00/tests/test_hello_agent.py -v

lint:
	uv run python -m compileall labs/00/src
