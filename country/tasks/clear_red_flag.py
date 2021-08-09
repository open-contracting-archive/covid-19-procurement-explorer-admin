from celery import Celery

from country.models import Tender

app = Celery()


@app.task(name="clear_red_flag")
def clear_red_flag(contract_id):
    tender = Tender.objects.get(id=contract_id)
    tender.red_flag.clear()
