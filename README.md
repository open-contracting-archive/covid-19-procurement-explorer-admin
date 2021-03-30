# COVID-19 Contract Explorer: Admin backend

## Getting started

Install development dependencies:

```shell
pip install pip-tools
pip-sync requirements_dev.txt
```

Set up the git pre-commit hook:

```shell
pre-commit install
```

Initialize the database:

```shell
createdb covid19_test
env DB_NAME=covid19_test ./manage.py migrate
```

Create a superuser:

```shell
env DB_NAME=covid19_test ./manage.py createsuperuser
```

Load test data:

```shell
env DB_NAME=covid19_test ./manage.py loaddata redflag
```

## Tasks

Run a development server:

```shell
env DEBUG=True DB_NAME=covid19_test ./manage.py runserver
```

To add, remove or upgrade a requirement, [follow these instructions](https://ocp-software-handbook.readthedocs.io/en/latest/python/applications.html#requirements).
