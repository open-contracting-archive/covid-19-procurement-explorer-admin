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
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer", None)
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            if buyer != "notnull":
                filter_args["contract__buyer__buyer_id"] = buyer
            else:
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
            data = {}
            data["product_name"] = goods["goods_services_category__category_name"]
            data["product_id"] = goods["goods_services_category__id"]
            if country:
                instance = Country.objects.get(country_code_alpha_2=country)
                data["local_currency_code"] = instance.currency
            else:
                data["local_currency_code"] = "USD"
            data["tender_count"] = goods["tender"]
            data["amount_local"] = goods["local"]
            data["amount_usd"] = goods["usd"]
            result.append(data)
        return JsonResponse(result, safe=False)
