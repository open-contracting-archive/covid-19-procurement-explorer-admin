from celery import Celery

from country.models import Buyer, Tender

app = Celery()


@app.task(name="delete_unused_buyers")
def delete_unused_buyers(country_code):
    buyer_ids = [
        buyer_id["buyer_id"]
        for buyer_id in Tender.objects.filter(country__country_code_alpha_2=country_code).values("buyer_id").distinct()
    ]
    buyers_to_delete = Buyer.objects.filter(country__country_code_alpha_2=country_code).exclude(id__in=buyer_ids)
    buyers_to_delete._raw_delete(buyers_to_delete.db)
    return "Done"
