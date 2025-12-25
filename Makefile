help:
	@echo " - lint           	: checks linting, fixes automatically if possible"
	@echo " - isort          	: sort imports alphabetically, by sections and type"
	@echo " - black          	: python code formatter"
	@echo " - clean           	: cleans the cache folders created by pytest and ruff"
	@echo " - format           	: runs isort + black + lint + clean"

lint: 
	poetry run python -m ruff core --fix

isort:
	poetry run python -m isort core

black:
	poetry run python -m black core

clean:
	sudo rm -rf __pycache__ .pytest_cache .ruff_cache

format: isort black lint clean