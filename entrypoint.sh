#!/bin/sh

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py crontab add

crond -b -l 8 -L /app/cron.log

python manage.py runserver 0.0.0.0:8000