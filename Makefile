dev:
	docker compose -f docker-compose.dev.yml down
	docker compose -f docker-compose.dev.yml up --build
run_tests:
	docker compose -f docker-compose.test.yml run --build --rm users-service poetry run pytest
	docker compose -f docker-compose.test.yml down -v
lint:
	docker build -t chack-check-users-lint -f docker/Dockerfile.lint .
	docker run --rm chack-check-users-lint
migrations:
	docker compose -f docker-compose.dev.yml run --build --rm users-service poetry run alembic revision --autogenerate -m "$(name)"
