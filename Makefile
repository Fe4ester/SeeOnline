# Управление контейнерным запуском

run:
	docker-compose up --build -d

stop:
	docker-compose stop

clean:
	docker-compose down

full-clean:
	docker-compose down --volumes
	docker system prune -af
	docker volume prune -f

restart: stop run

rebuild: clean run

# Управление воркерами

worker:
	celery -A SeeOnline worker --loglevel=warning --logfile=celery_logs.log

beat:
	celery -A SeeOnline beat --loglevel=warning --logfile=beat_logs.log