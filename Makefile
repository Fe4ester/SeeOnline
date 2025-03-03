# Управление контейнерным запуском
.PHONY: build run start stop remove logs

APP_NAME = seeonline-app
DB_NAME = seeonline-db
NETWORK_NAME = monitoring

build:
	docker build -t $(APP_NAME) .

run:
	docker network inspect $(NETWORK_NAME) >/dev/null 2>&1 || docker network create $(NETWORK_NAME)
	docker run --network $(NETWORK_NAME) --name $(APP_NAME) -p 8000:8000 -d $(APP_NAME)

start:
	docker start $(APP_NAME)

stop:
	docker stop $(APP_NAME)

remove:
	make stop
	docker rm $(APP_NAME)

logs:
	docker logs -f $(APP_NAME)


# Управление воркерами Celery
.PHONY: worker beat

worker:
	celery -A SeeOnline worker --loglevel=error

beat:
	celery -A SeeOnline beat --loglevel=error


# Управление базой данных (локальная)
.PHONY: run-db start-db stop-db remove-db db-logs

run-db:
	docker network inspect $(NETWORK_NAME) >/dev/null 2>&1 || docker network create $(NETWORK_NAME)
	docker run --network $(NETWORK_NAME) --name $(DB_NAME) -p 5432:5432 \
		-e POSTGRES_USER=postgres \
		-e POSTGRES_PASSWORD=256643 \
		-e POSTGRES_DB=seeonline \
		-d postgres

start-db:
	docker start $(DB_NAME)

stop-db:
	docker stop $(DB_NAME)

remove-db:
	make stop-db
	docker rm $(DB_NAME)

db-logs:
	docker logs -f $(DB_NAME)


# Метрики и визуализация
.PHONY: run-prometheus run-grafana start-prometheus start-grafana stop-prometheus stop-grafana remove-prometheus remove-grafana

PROMETHEUS_NAME = prometheus
GRAFANA_NAME = grafana
GRAFANA_STORAGE = grafana-storage
PROMETHEUS_CONFIG = $(PWD)/prometheus.yml

run-prometheus:
	docker network inspect $(NETWORK_NAME) >/dev/null 2>&1 || docker network create $(NETWORK_NAME)
	docker run -d --name $(PROMETHEUS_NAME) --network $(NETWORK_NAME) -p 9090:9090 \
		-v $(PROMETHEUS_CONFIG):/etc/prometheus/prometheus.yml prom/prometheus

run-grafana:
	docker network inspect $(NETWORK_NAME) >/dev/null 2>&1 || docker network create $(NETWORK_NAME)
	docker run -d --name $(GRAFANA_NAME) --network $(NETWORK_NAME) -p 3000:3000 \
		-v $(GRAFANA_STORAGE):/var/lib/grafana grafana/grafana

start-prometheus:
	docker start $(PROMETHEUS_NAME)

start-grafana:
	docker start $(GRAFANA_NAME)

stop-prometheus:
	docker stop $(PROMETHEUS_NAME)

stop-grafana:
	docker stop $(GRAFANA_NAME)

remove-prometheus:
	make stop-prometheus
	docker rm $(PROMETHEUS_NAME)

remove-grafana:
	make stop-grafana
	docker rm $(GRAFANA_NAME)
