from django.db.models import F
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Buyer
from visualization.helpers.general import page_expire_period


def top_buyer(order_by, **filter_args):
    result = (
        Buyer.objects.filter(**filter_args)
        .values("id", "buyer_name", "country__currency")
        .annotate(
            tender_count=F("summary__tender_count"),
            amount_usd=F("summary__amount_usd"),
            amount_local=F("summary__amount_local"),
        )
        .order_by(f"-{order_by}")[:10]
    )

    return result


def formatted(data):
    return {
        "amount_local": data["amount_local"] if data["amount_local"] else 0,
        "amount_usd": data["amount_usd"] or 0,
        "local_currency_code": data["country__currency"],
        "buyer_id": data["id"],
        "buyer_name": data["buyer_name"],
        "tender_count": data["tender_count"] if data["tender_count"] else 0,
    }


class TopBuyers(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        country_code = self.request.GET.get("country", None)
        supplier_id = self.request.GET.get("supplier")
        filter_args = {
            "country__isnull": False,
            "summary__tender_count__isnull": False,
            "summary__amount_local__isnull": False,
            "summary__amount_usd__isnull": False,
        }

        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code

        if supplier_id:
            filter_args["tenders__supplier_id"] = supplier_id

        for_value = top_buyer(order_by="amount_usd", **filter_args)
        for_number = top_buyer(order_by="tender_count", **filter_args)
        by_number = []
        by_value = []

        for value in for_value:
            by_value.append(formatted(value))

        for value in for_number:
            by_number.append(formatted(value))

        return JsonResponse({"by_number": by_number, "by_value": by_value})
