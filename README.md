# Backend
API URL: `https://cap-api.gura.ch/`

## Run

### Initialization

```bash
$ pip install pipenv
$ pipenv install --system --deploy --ignore-pipfile
$ python manage.py makemigrations tracker
$ python manage.py makemigrations user
$ python manage.py makemigrations visualize
$ python manage.py migrate
$ python manage.py createsuperuser --email admin@example.com --username admin
$ python manage.py crontab add
```

registered admin
```yaml
Username: admin
Password: pddyrfFkYW0nAb1BKJ1LVb5Ftov1xo8O/KCjgva2cCPqzcmBnaK5lXwd8pNbhMBe
Email: admin@example.com
```

Note: To enable automatically retrieve data, the system must be **Linux** and have **cron** enabled

### After Initialization

#### Linux

```bash
$ python manage.py runserver 0.0.0.0:8000
```

#### docker-compose

```yaml
version: "3.8"
services:
    backend:
        build: ./backend
        container_name: backend_container
        hostname: Halyul-Server-Docker
        volumes:
            - ./:/app
        environment:
            ENV: production
        ports:
            - 8000:8000
        restart: always
        logging:
            driver: "json-file"
            options:
                max-size: "1g"
                max-file: "1"
```

##### Note

Superuser will not be created in `docker` container. Run following command in the container:

```bash
$ python manage.py createsuperuser --email admin@example.com --username admin
```