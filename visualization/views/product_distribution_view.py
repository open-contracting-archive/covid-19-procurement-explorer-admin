from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, GoodsServices
from visualization.helpers.general import page_expire_period


class ProductDistributionView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        country_code = self.request.GET.get("country", None)
        buyer_id = self.request.GET.get("buyer", None)
        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code
        if buyer_id:
            filter_args["contract__buyer__buyer_id"] = buyer_id
            if buyer_id == "notnull":
                filter_args["contract__buyer__isnull"] = False

        result = []
        goods_services = (
            GoodsServices.objects.filter(**filter_args)
            .values("goods_services_category__category_name", "goods_services_category__id")
            .annotate(
                tender=Count("goods_services_category"),
                local=Sum("contract_value_local"),
                usd=Sum("contract_value_usd"),
            )
        )
        for goods in goods_services:
            data = {
                "product_name": goods["goods_services_category__category_name"],
                "product_id": goods["goods_services_category__id"],
                "local_currency_code": "USD",
            }
            if country_code:
                instance = Country.objects.get(country_code_alpha_2=country_code)
                data["local_currency_code"] = instance.currency

            data["tender_count"] = goods["tender"]
            data["amount_local"] = goods["local"]
            data["amount_usd"] = goods["usd"]
            result.append(data)
        return JsonResponse(result, safe=False)
