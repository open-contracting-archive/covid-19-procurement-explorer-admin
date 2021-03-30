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

```
createdb covid19_test
env DB_NAME=covid19_test ./manage.py migrate
```
