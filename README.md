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

Change `CSRF_TRUSTED_ORIGINS` in `api/env/production.py` to access `/admin`

Note: To enable automatically retrieve data, the system must be **Linux** and have **crond/crontab/cron** enabled

### After Initialization

#### Linux

```bash
$ python manage.py runserver 0.0.0.0:8000
```

#### docker-compose

**NO INITIALIZATION NEEDED**

```yaml
version: "3.8"
services:
    backend:
        build: ./
        container_name: backend_container
        volumes:
            - ./:/app
        environment:
            ENV: production
            ADMIN_EMAIL: admin@example.com
            ADMIN_PASSWORD: pddyrfFkYW0nAb1BKJ1LVb5Ftov1xo8O/KCjgva2cCPqzcmBnaK5lXwd8pNbhMBe
            ADMIN_USERNAME: admin
            ADMIN_FIRST_NAME: admin
            ADMIN_LAST_NAME: admin
        restart: always
        logging:
            driver: "json-file"
            options:
                max-size: "1g"
                max-file: "1"
```
