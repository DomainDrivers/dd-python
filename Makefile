qa:
	ruff check . --extend-select I --fix
	ruff format .
	mypy --strict --enable-incomplete-feature=NewGenericSyntax .
	pytest tests/
	tach check
