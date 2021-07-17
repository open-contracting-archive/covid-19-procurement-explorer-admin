from celery import Celery

from country.models import Tender

app = Celery()


@app.task(name="clear_redflag")
def clear_redflag(id):
    tender = Tender.objects.get(id=id)
    tender.red_flag.clear()
    print(f"end of {id}")
