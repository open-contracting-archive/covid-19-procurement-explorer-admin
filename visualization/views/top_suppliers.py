from django.db.models import Count, F
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


def top_supplier(order_by, **filter_args):
    result = (
        Tender.objects.filter(**filter_args)
        .values("supplier__id", "supplier__supplier_name", "country__currency")
        .annotate(
            count=Count("id"),
            usd=F("contract_value_usd"),
            local=F("contract_value_local"),
        )
        .order_by(f"-{order_by}")[:10]
    )

    return result


class TopSuppliers(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        country_code = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")

        filter_args = {"supplier__isnull": False, "contract_value_usd__isnull": False}

        if country_code:
            filter_args["country__country_code_alpha_2"] = country_code

        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)

        for_value = top_supplier(order_by="usd", **filter_args)
        for_number = top_supplier(order_by="count", **filter_args)
        by_number = []
        by_value = []
        by_buyer = []

        for_buyer = (
            Tender.objects.filter(**filter_args)
            .values("supplier__id", "supplier__supplier_name", "country__currency")
            .annotate(count=Count("buyer__id", distinct=True))
            .order_by("-count")[:10]
        )

        for value in for_value:
            a = {
                "amount_local": value["local"] if value["local"] else 0,
                "amount_usd": value["usd"] if value["usd"] else 0,
                "local_currency_code": value["country__currency"],
                "supplier_id": value["supplier__id"],
                "supplier_name": value["supplier__supplier_name"],
                "tender_count": value["count"],
            }
            by_value.append(a)

        for value in for_number:
            a = {
                "amount_local": value["local"] if value["local"] else 0,
                "amount_usd": value["usd"] if value["usd"] else 0,
                "local_currency_code": value["country__currency"],
                "supplier_id": value["supplier__id"],
                "supplier_name": value["supplier__supplier_name"],
                "tender_count": value["count"],
            }
            by_number.append(a)

        for value in for_buyer:
            a = {
                "supplier_id": value["supplier__id"],
                "local_currency_code": value["country__currency"],
                "supplier_name": value["supplier__supplier_name"],
                "buyer_count": value["count"],
            }
            by_buyer.append(a)

        return JsonResponse({"by_number": by_number, "by_value": by_value, "by_buyer": by_buyer})
