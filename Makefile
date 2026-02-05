help:
	@echo " - lint              : checks linting, fixes automatically if possible"
	@echo " - isort             : sort imports alphabetically, by sections and type"
	@echo " - black             : python code formatter"
	@echo " - clean             : cleans the cache folders created by pytest and ruff"
	@echo " - format            : runs isort + black + lint + clean"
	@echo " - build             : builds the docker image called 'rudder:latest'"
	@echo " - run               : runs the docker containers and starts the dialog system"
	@echo " - verify-llm        : verifies that the llm client is working"
	@echo " - down              : stops all the docker containers"
	@echo ""
	@echo "Demo scripts:"
	@echo " - demo-balance      : run balance inquiry demo"
	@echo " - demo-transactions : run transaction query demo"
	@echo " - demo-transfer     : run transfer flow demo"
	@echo " - demo-full         : run full conversation demo"
	@echo " - demo-interactive  : run interactive chat demo"

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

# Demo targets
demo-balance:
	docker compose up -d
	docker compose exec app python demos/demo_balance.py

demo-transactions:
	docker compose up -d
	docker compose exec app python demos/demo_transactions.py

demo-transfer:
	docker compose up -d
	docker compose exec app python demos/demo_transfer.py

demo-full:
	docker compose up -d
	docker compose exec app python demos/demo_full_conversation.py

demo-interactive:
	docker compose up -d
	docker compose exec -it app python demos/demo_interactive.py
