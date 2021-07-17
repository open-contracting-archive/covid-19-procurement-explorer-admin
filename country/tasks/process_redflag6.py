from celery import Celery

from country.models import RedFlag, Tender

app = Celery()


@app.task(name="process_red_flag6")
def process_redflag6(id):
    flag6_obj = RedFlag.objects.get(function_name="flag6")
    tenders = Tender.objects.filter(id=id).values(
        "id", "buyer__buyer_name", "supplier__supplier_name", "supplier__supplier_address"
    )
    for tender in tenders:
        a = (
            Tender.objects.values("buyer__buyer_name")
            .filter(
                supplier__supplier_name=tender["supplier__supplier_name"],
                supplier__supplier_address=tender["supplier__supplier_address"],
            )
            .distinct("buyer__buyer_name")
        )
        if len(a) > 2:
            if a[0]["buyer__buyer_name"] == a[1]["buyer__buyer_name"]:
                for obj in a:
                    objs = Tender.objects.get(id=obj.id)
                    objs.red_flag.add(flag6_obj)
