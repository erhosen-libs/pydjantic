bump_version:
	@poetry version minor

clean:
	@rm -rf build dist .eggs *.egg-info
	@rm -rf .coverage coverage.xml htmlcov report.xml .tox
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type f -name "*.py[co]" -exec rm -rf {} +

format: clean
	@pre-commit run --all-files

test:
	@python -m pytest --cov=pydjantic tests/ -sq

build: test clean
	@poetry build

publish:
	@poetry publish

# How to release:
# 1) git pull
# 2) make bump_version
# 3) update __version__ var in pydjantic/__init__.py
# 4) make build
# 5) make publish
