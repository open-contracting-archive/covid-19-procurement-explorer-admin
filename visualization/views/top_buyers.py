from django.db.models import Count, F
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


def top_buyer(order_by, **filter_args):
    result = (
        Tender.objects.filter(**filter_args)
        .values("buyer__id", "buyer__buyer_name", "country__currency")
        .annotate(
            count=Count("id"),
            usd=F("contract_value_usd"),
            local=F("contract_value_local"),
        )
        .order_by(f"-{order_by}")[:10]
    )

    return result


class TopBuyers(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        country_code = self.request.GET.get("country", None)
        supplier = self.request.GET.get("supplier")
        filter_args = {
            "buyer__isnull": False,
            "contract_value_usd__isnull": False,
        }

        if country_code:
            filter_args["country__country_code_alpha_2"] = country_code

        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)

        for_value = top_buyer(order_by="usd", **filter_args)
        for_number = top_buyer(order_by="count", **filter_args)
        by_number = []
        by_value = []

        for value in for_value:
            a = {
                "amount_local": value["local"] if value["usd"] else 0,
                "amount_usd": value["usd"] or 0,
                "local_currency_code": value["country__currency"],
                "buyer_id": value["buyer__id"],
                "buyer_name": value["buyer__buyer_name"],
                "tender_count": value["count"],
            }
            by_value.append(a)

        for value in for_number:
            a = {
                "amount_local": value["local"] if value["usd"] else 0,
                "amount_usd": value["usd"] or 0,
                "local_currency_code": value["country__currency"],
                "buyer_id": value["buyer__id"],
                "buyer_name": value["buyer__buyer_name"],
                "tender_count": value["count"],
            }
            by_number.append(a)

        return JsonResponse({"by_number": by_number, "by_value": by_value})
