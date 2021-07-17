from collections import defaultdict

from celery import Celery

from country.models import RedFlag, Tender

app = Celery()


@app.task(name="process_red_flag7")
def process_redflag7(id):
    tender = Tender.objects.filter(id=id).values("supplier_id").first()
    supplier_tenders = list(
        Tender.objects.filter(supplier=tender["supplier_id"]).values("id", "supplier_id", "buyer_id")
    )
    total_tenders = len(supplier_tenders)
    if total_tenders > 10:
        grouped_list = defaultdict(list)
        for item in supplier_tenders:
            grouped_list[item["buyer_id"]].append(item)
        parsed_list = [{"name": key, "data": value, "count": len(value)} for key, value in grouped_list.items()]

        final_list = []
        for group in parsed_list:
            if group["count"] > 10 and (((group["count"] / total_tenders) * 100) > 50):
                for tender in group["data"]:
                    final_list.append(tender["id"])
        if len(final_list) > 0:
            flag7_obj = RedFlag.objects.get(function_name="flag7")
            # supplier who has signed X(50) percent or more of their contracts with the same buyer
            # (wins tenders from the same buyer)
            flag7_obj.tender_set.add(*final_list)
