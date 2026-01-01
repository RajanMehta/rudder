help:
	@echo " - lint           	: checks linting, fixes automatically if possible"
	@echo " - isort          	: sort imports alphabetically, by sections and type"
	@echo " - black          	: python code formatter"
	@echo " - clean           	: cleans the cache folders created by pytest and ruff"
	@echo " - format           	: runs isort + black + lint + clean"
	@echo " - build           	: builds the docker image called 'rudder:latest'"
	@echo " - run             	: runs the docker containers and starts the dialog system"
	@echo " - verify-llm      	: verifies that the llm client is working"
	@echo " - down            	: stops all the docker containers"

lint:
	poetry run python -m ruff core --fix

isort:
	poetry run python -m isort core

black:
	poetry run python -m black core

clean:
	sudo rm -rf __pycache__ .pytest_cache .ruff_cache

format: isort black lint clean

build:
	docker compose build

run:
	docker compose up -d
	docker compose exec -it app python main.py

verify-llm:
	docker compose run --rm -e PYTHONPATH=/app app python tests/verify_llm_client.py

down:
	docker compose down
