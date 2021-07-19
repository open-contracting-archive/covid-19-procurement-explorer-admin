from celery import Celery

from country.models import Country, Tender
from country.tasks.clear_redflag import clear_redflag
from country.tasks.process_redflag import process_redflag
from country.tasks.process_redflag6 import process_redflag6
from country.tasks.process_redflag7 import process_redflag7

app = Celery()


@app.task(name="evaluate_contract_red_flag")
def evaluate_contract_red_flag(country_code):
    country = Country.objects.get(country_code_alpha_2=country_code)
    country_tenders = Tender.objects.filter(country_id=country.id, supplier__isnull=False, buyer__isnull=False)
    for tender in country_tenders:
        tender_id = tender.id
        clear_redflag.apply_async(args=(tender_id,), queue="covid19")
        process_redflag6.apply_async(args=(tender_id,), queue="covid19")
        process_redflag7.apply_async(args=(tender_id,), queue="covid19")
        process_redflag.apply_async(args=(tender_id,), queue="covid19")
