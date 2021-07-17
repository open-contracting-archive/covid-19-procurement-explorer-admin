from celery import Celery
from django.db.models import Count, Q, Sum

from country.models import Buyer

app = Celery()


@app.task(name="summarize_buyer")
def summarize_buyer(buyer_id):
    buyer_summary_general = (
        Buyer.objects.filter(id=buyer_id)
        .values("tenders__country__country_code_alpha_2", "tenders__country__name")
        .annotate(
            amount_usd=Sum("tenders__contract_value_usd"),
            amount_local=Sum("tenders__contract_value_local"),
            tender_count=Count("tenders__id", distinct=True),
        )
        .first()
    )
    buyer_summary_other = (
        Buyer.objects.filter(id=buyer_id)
        .values("id")
        .annotate(
            supplier_count=Count("tenders__supplier_id", filter=Q(tenders__supplier_id__isnull=False), distinct=True),
            product_count=Count("tenders__goods_services__goods_services_category", distinct=True),
            red_flag_count=Count("tenders__red_flag", distinct=True),
        )
        .first()
    )
    summary = {
        "amount_local": buyer_summary_general["amount_local"],
        "amount_usd": buyer_summary_general["amount_usd"],
        "tender_count": buyer_summary_general["tender_count"],
        "country_code": buyer_summary_general["tenders__country__country_code_alpha_2"],
        "country_name": buyer_summary_general["tenders__country__name"],
        "supplier_count": buyer_summary_other["supplier_count"],
        "product_count": buyer_summary_other["product_count"],
        "red_flag_tender_count": buyer_summary_other["red_flag_count"],
        "red_flag_tender_percentage": 0
        if buyer_summary_general["tender_count"] == 0
        else float(buyer_summary_other["red_flag_count"] / buyer_summary_general["tender_count"]),
    }
    try:
        buyer = Buyer.objects.get(id=buyer_id)
        buyer.summary = summary
        buyer.save()
    except Exception:
        return "Buyer id doesnt exists!"
    return "Completed"
