.PHONY: models up down logs lint test test-py test-java test-e2e test-k6 coverage clean

models:
	./scripts/bootstrap_models.sh

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

lint:
	python3 -m compileall ai-service/app
	cd backend-java && mvn -q -DskipTests package
	npm --prefix frontend install
	npm --prefix frontend run lint

test: test-py test-java

test-py:
	./tests/scripts/run_python_tests.sh

test-java:
	./tests/scripts/run_java_tests.sh

test-e2e:
	./tests/scripts/run_e2e_tests.sh

test-k6:
	./tests/scripts/run_k6_load.sh

coverage: test
	@echo "Coverage artifacts available under tests/coverage"

clean:
	rm -rf tests/coverage/* backend-java/target frontend/node_modules frontend/dist tests/e2e/node_modules
