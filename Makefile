#run:
#	docker-compose up -d --build
#
#stop:
#	docker-compose stop
#
#csu:
#	docker exec -it name python manage.py createsuperuser
#
#migrate:
#	docker exec -it name python manage.py migrate

run:
	python manage.py runserver

# django's tests, for pytest I use `$ pytest` :)
test:
	python manage.py test

csu:
	python manage.py createsuperuser

migrate:
	python manage.py migrate

makemigrations:
	python manage.py migrate
