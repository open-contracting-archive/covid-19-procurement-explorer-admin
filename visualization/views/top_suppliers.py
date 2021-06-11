from django.contrib.postgres.fields.jsonb import KeyTransform
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Supplier
from visualization.helpers.general import page_expire_period


def top_supplier(order_by, **filter_args):
    result = (
        Supplier.objects.filter(**filter_args)
        .values("id", "supplier_name", "country__currency")
        .annotate(
            tender_count=KeyTransform("tender_count", "summary__tender_count"),
            amount_usd=KeyTransform("amount_usd", "summary__amount_usd"),
            amount_local=KeyTransform("amount_local", "summary__amount_local"),
            buyer_count=KeyTransform("buyer_count", "summary__buyer_count"),
        )
        .order_by(f"-{order_by}")[:10]
    )

    return result


class TopSuppliers(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        country_code = self.request.GET.get("country", None)
        buyer_id = self.request.GET.get("buyer")

        filter_args = {
            "country__isnull": False,
            "summary__tender_count__isnull": False,
            "summary__amount_local__isnull": False,
            "summary__amount_usd__isnull": False,
        }

        if country_code:
            filter_args["country__country_code_alpha_2"] = country_code

        if buyer_id:
            filter_args["tenders__buyer_id"] = buyer_id

        for_value = top_supplier(order_by="amount_usd", **filter_args)
        for_number = top_supplier(order_by="tender_count", **filter_args)
        for_buyer = top_supplier(order_by="buyer_count", **filter_args)
        by_number = []
        by_value = []
        by_buyer = []

        for value in for_value:
            a = {
                "amount_local": value["amount_local"] if value["amount_local"] else 0,
                "amount_usd": value["amount_usd"] or 0,
                "local_currency_code": value["country__currency"],
                "supplier_id": value["id"],
                "supplier_name": value["supplier_name"],
                "tender_count": value["tender_count"] if value["tender_count"] else 0,
            }
            by_value.append(a)

        for value in for_number:
            a = {
                "amount_local": value["amount_local"] if value["amount_local"] else 0,
                "amount_usd": value["amount_usd"] or 0,
                "local_currency_code": value["country__currency"],
                "supplier_id": value["id"],
                "supplier_name": value["supplier_name"],
                "tender_count": value["tender_count"] if value["tender_count"] else 0,
            }
            by_number.append(a)

        for value in for_buyer:
            a = {
                "buyer_count": value["buyer_count"],
                "supplier_id": value["id"],
                "supplier_name": value["supplier_name"],
            }
            by_buyer.append(a)

        return JsonResponse({"by_number": by_number, "by_value": by_value, "by_buyer": by_buyer})
