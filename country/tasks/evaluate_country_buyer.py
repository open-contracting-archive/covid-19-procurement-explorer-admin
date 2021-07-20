from celery import Celery

from country.models import Buyer
from country.tasks.summarize_buyer import summarize_buyer

app = Celery()


@app.task(name="evaluate_country_buyer")
def evaluate_country_buyer(country_code):
    buyers = Buyer.objects.filter(country__country_code_alpha_2=country_code)

    for buyer in buyers:
        summarize_buyer(buyer.id)

    return True
