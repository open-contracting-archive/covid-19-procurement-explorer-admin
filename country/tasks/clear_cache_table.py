from celery import Celery
from django.core.cache import cache

app = Celery()


@app.task(name="clear_cache_table")
def clear_cache_table():
    cache.clear()
