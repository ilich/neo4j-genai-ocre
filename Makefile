.PHONY: install run run-rq test
.DEFAULT_GOAL := run

install:
	uv sync

run:
	uv run mcp_server.py