from celery import Celery

from country.models import Supplier, Tender

app = Celery()


@app.task(name="delete_unused_suppliers")
def delete_unused_suppliers(country_code):
    supplier_ids = [
        supplier_id["supplier_id"]
        for supplier_id in Tender.objects.filter(country__country_code_alpha_2=country_code)
        .values("supplier_id")
        .distinct()
    ]
    suppliers_to_delete = Supplier.objects.filter(country__country_code_alpha_2=country_code).exclude(
        id__in=supplier_ids
    )
    suppliers_to_delete._raw_delete(suppliers_to_delete.db)
    return "Done"
