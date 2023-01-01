venv: pyproject.toml
	python3 -m venv .venv && .venv/bin/pip3 install poetry && .venv/bin/poetry install --no-root

cleanup: .venv
	rm -rf .venv
