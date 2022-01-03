FROM python:alpine

ADD VERSION .

WORKDIR /app

RUN pip install pipenv

COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock
RUN pipenv install --system --deploy --ignore-pipfile

COPY . /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]