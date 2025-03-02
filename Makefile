# Управление контейнерным запуском

build:
	docker build -t seeonline-app .

run:
	docker run --network monitoring --name seeonline-app -p 8000:8000 -d seeonline-app

start:
	docker start seeonline-app

stop:
	docker stop seeonline-app

remove:
	make stop
	docker rm seeonline-app


# Управление воркерами

worker:
	celery -A SeeOnline worker --loglevel=info

beat:
	celery -A SeeOnline beat --loglevel=info


# База данных(локальная
run-db:
	docker run --network monitoring --name seeonline-db -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=256643 -e POSTGRES_DB=seeonline -d postgres


start-db:
	docker start seeonline-db


stop-db:
	docker stop seeonline-db


remove-db:
	make stop-db
	docker rm seeonline-db

# Метрики и визуализация


run-prometheus:
	docker run -d --name prometheus --network monitoring -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus


run-grafana:
	docker run -d --name grafana --network monitoring -p 3000:3000 -v grafana-storage:/var/lib/grafana grafana/grafana


start-prometheus:
	docker start prometheus


start-grafana:
	docker start grafana


stop-prometheus:
	docker stop prometheus


stop-grafana:
	docker stop grafana


remove-prometheus:
	make stop-prometheus
	docker rm promethes


remove-grafana:
	make stop-grafana
	docker rm grafana