from celery import Celery

from country.models import Supplier
from country.tasks import summarize_supplier

app = Celery()


@app.task(name="evaluate_country_supplier")
def evaluate_country_supplier(country_code):
    suppliers = Supplier.objects.filter(country__country_code_alpha_2=country_code)

    for supplier in suppliers:
        summarize_supplier(supplier.id)

    return True
