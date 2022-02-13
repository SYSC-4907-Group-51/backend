FROM python:alpine

ADD VERSION .
ENV ADMIN_EMAIL $ADMIN_EMAIL
ENV ADMIN_PASSWORD $ADMIN_PASSWORD
ENV ADMIN_USERNAME $ADMIN_USERNAME  
ENV ADMIN_FIRST_NAME $ADMIN_FIRST_NAME
ENV ADMIN_LAST_NAME $ADMIN_LAST_NAME

WORKDIR /app

RUN pip install pipenv

COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock
RUN pipenv install --system --deploy --ignore-pipfile

COPY . /app

RUN python manage.py makemigrations tracker && \
    python manage.py makemigrations user && \
    python manage.py makemigrations visualize && \
    python manage.py migrate && \
    python manage.py crontab add && \  
    python manage.py collectstatic --noinput && \
    python manage.py createsuperuser --email ${ADMIN_EMAIL} --username ${ADMIN_USERNAME} --first_name ${ADMIN_FIRST_NAME} --last_name ${ADMIN_LAST_NAME} --password ${ADMIN_PASSWORD} --noinput

RUN crond -b -l 8 -L /app/cron.log

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]