# Running tests

## Prerequisites

- Install [Python3.12](https://www.python.org/downloads/)
- Install [poetry](https://python-poetry.org/)
- Install project dependencies in a poetry's managed virtualenv `poetry install --with=dev`
- Have docker up and running (tests use [TestContainers](https://testcontainers.com/))

## Running linters and tests

### If you have make
```bash
make qa
```

### If you don't have make
```bash
ruff check . --extend-select I --fix
ruff format .
mypy --strict --enable-incomplete-feature=NewGenericSyntax .
pytest tests/
tach check
```

