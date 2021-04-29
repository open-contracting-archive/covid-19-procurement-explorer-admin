from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class TopSuppliers(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        filter_args = {}
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        filter_args["supplier__isnull"] = False
        filter_args["goods_services__contract_value_usd__isnull"] = False
        for_value = (
            Tender.objects.filter(**filter_args)
            .values("supplier__id", "supplier__supplier_name", "country__currency")
            .annotate(
                count=Count("id"),
                usd=Sum("goods_services__contract_value_usd"),
                local=Sum("goods_services__contract_value_local"),
            )
            .exclude(usd__isnull=True)
            .order_by("-usd")[:10]
        )
        for_number = (
            Tender.objects.filter(**filter_args)
            .exclude(goods_services__contract_value_usd__isnull=True)
            .values("supplier__id", "supplier__supplier_name", "country__currency")
            .annotate(
                count=Count("goods_services__contract__id", distinct=True),
                usd=Sum("goods_services__contract_value_usd"),
                local=Sum("goods_services__contract_value_local"),
            )
            .exclude(usd__isnull=True)
            .order_by("-count")[:10]
        )
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
            a = {}
            a["amount_local"] = value["local"] if value["local"] else 0
            a["amount_usd"] = value["usd"] if value["usd"] else 0
            a["local_currency_code"] = value["country__currency"]
            a["supplier_id"] = value["supplier__id"]
            a["supplier_name"] = value["supplier__supplier_name"]
            a["tender_count"] = value["count"]
            by_value.append(a)
        for value in for_number:
            a = {}
            a["amount_local"] = value["local"] if value["local"] else 0
            a["amount_usd"] = value["usd"] if value["usd"] else 0
            a["local_currency_code"] = value["country__currency"]
            a["supplier_id"] = value["supplier__id"]
            a["supplier_name"] = value["supplier__supplier_name"]
            a["tender_count"] = value["count"]
            by_number.append(a)

        for value in for_buyer:
            a = {}
            a["supplier_id"] = value["supplier__id"]
            a["local_currency_code"] = value["country__currency"]
            a["supplier_name"] = value["supplier__supplier_name"]
            a["buyer_count"] = value["count"]
            by_buyer.append(a)

        return JsonResponse({"by_number": by_number, "by_value": by_value, "by_buyer": by_buyer})
