from celery import Celery
from django.db.models import Count, Q, Sum

from country.models import Supplier

app = Celery()


@app.task(name="summarize_supplier")
def summarize_supplier(supplier_id):
    supplier_summary_general = (
        Supplier.objects.filter(id=supplier_id)
        .values("tenders__country__country_code_alpha_2", "tenders__country__name")
        .annotate(
            amount_usd=Sum("tenders__contract_value_usd"),
            amount_local=Sum("tenders__contract_value_local"),
            tender_count=Count("tenders__id", distinct=True),
        )
        .first()
    )
    supplier_summary_other = (
        Supplier.objects.filter(id=supplier_id)
        .values("id")
        .annotate(
            buyer_count=Count("tenders__buyer_id", filter=Q(tenders__buyer_id__isnull=False), distinct=True),
            product_count=Count("tenders__goods_services__goods_services_category", distinct=True),
            red_flag_count=Count("tenders__red_flag", distinct=True),
        )
        .first()
    )
    summary = {
        "amount_local": supplier_summary_general["amount_local"],
        "amount_usd": supplier_summary_general["amount_usd"],
        "tender_count": supplier_summary_general["tender_count"],
        "country_code": supplier_summary_general["tenders__country__country_code_alpha_2"],
        "country_name": supplier_summary_general["tenders__country__name"],
        "buyer_count": supplier_summary_other["buyer_count"],
        "product_count": supplier_summary_other["product_count"],
        "red_flag_tender_count": supplier_summary_other["red_flag_count"],
        "red_flag_tender_percentage": 0
        if supplier_summary_general["tender_count"] == 0
        else float(supplier_summary_other["red_flag_count"] / supplier_summary_general["tender_count"]),
    }

    try:
        supplier = Supplier.objects.get(id=supplier_id)
        supplier.summary = summary
        supplier.save()
    except Exception as e:
        return e
    return "Completed"
