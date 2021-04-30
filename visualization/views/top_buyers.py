from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class TopBuyers(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        country = self.request.GET.get("country", None)
        supplier = self.request.GET.get("supplier")

        filter_args = {}
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)
        filter_args["buyer__isnull"] = False
        filter_args["goods_services__contract_value_usd__isnull"] = False
        for_value = (
            Tender.objects.filter(**filter_args)
            .values("buyer__id", "buyer__buyer_name", "country__currency")
            .annotate(
                count=Count("id"),
                usd=Sum("goods_services__contract_value_usd"),
                local=Sum("goods_services__contract_value_local"),
            )
            .order_by("-usd")[:10]
        )
        for_number = (
            Tender.objects.filter(**filter_args)
            .exclude(goods_services__contract_value_usd__isnull=True)
            .values("buyer__id", "buyer__buyer_name", "country__currency")
            .annotate(
                count=Count("goods_services__contract__id", distinct=True),
                usd=Sum("goods_services__contract_value_usd"),
                local=Sum("goods_services__contract_value_local"),
            )
            .order_by("-count")[:10]
        )
        by_number = []
        by_value = []
        for value in for_value:
            a = {
                "amount_local": value["local"] if value["usd"] else 0,
                "amount_usd": value["usd"] if value["usd"] else 0,
                "local_currency_code": value["country__currency"],
                "buyer_id": value["buyer__id"],
                "buyer_name": value["buyer__buyer_name"],
                "tender_count": value["count"],
            }
            by_value.append(a)
        for value in for_number:
            a = {
                "amount_local": value["local"] if value["usd"] else 0,
                "amount_usd": value["usd"] if value["usd"] else 0,
                "local_currency_code": value["country__currency"],
                "buyer_id": value["buyer__id"],
                "buyer_name": value["buyer__buyer_name"],
                "tender_count": value["count"],
            }
            by_number.append(a)
        return JsonResponse({"by_number": by_number, "by_value": by_value})
