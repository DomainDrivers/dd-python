qa:
	ruff format .
	ruff check . --fix
	mypy --strict --enable-incomplete-feature=NewGenericSyntax .
	pytest tests/
	tach check
