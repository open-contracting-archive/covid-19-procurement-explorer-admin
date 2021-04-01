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
./manage.py migrate
```

Create a superuser:

```shell
./manage.py createsuperuser
```

Load test data:

```shell
./manage.py loaddata country redflag equitycategory equitykeywords
```

Retrieve remote data:

```shell
env DB_NAME=covid19_test ./manage.py fetch_covid_active_cases
```

## Tasks

Run a development server:

```shell
env DEBUG=True ./manage.py runserver
```

To add, remove or upgrade a requirement, [follow these instructions](https://ocp-software-handbook.readthedocs.io/en/latest/python/applications.html#requirements).
