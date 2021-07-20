from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, EquityCategory, GoodsServicesCategory, RedFlag
from helpers.general import page_expire_period


class FilterParametersStatic(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        countries = Country.objects.values("id", "country_code", "name")
        products = GoodsServicesCategory.objects.values("id", "category_name")
        equities = EquityCategory.objects.values("id", "category_name")
        red_flags = RedFlag.objects.filter(implemented=True).values("id", "title")
        result_country = []
        result_product = []
        result_equity = []
        result_red_flag = []
        result = {}
        if countries:
            result_country = [
                {"id": country["id"], "code": country["country_code"], "name": country["name"]}
                for country in countries
            ]

        if products:
            result_product = [{"id": product["id"], "name": product["category_name"]} for product in products]

        if equities:
            result_equity = [{"id": equity["id"], "name": equity["category_name"]} for equity in equities]
        if red_flags:
            result_red_flag = [{"id": red_flag["id"], "name": red_flag["title"]} for red_flag in red_flags]
        result["method"] = [
            {"label": "Direct", "value": "direct"},
            {"label": "Limited", "value": "limited"},
            {"label": "Open", "value": "open"},
            {"label": "Other", "value": "other"},
            {"label": "Selective", "value": "selective"},
            {"label": "Not Identified", "value": "not_identified"},
        ]
        result["status"] = [
            {"label": "Active", "value": "active"},
            {"label": "Cancelled", "value": "cancelled"},
            {"label": "Completed", "value": "completed"},
            {"label": "Other", "value": "other"},
            {"label": "Not Identified", "value": "not_identified"},
        ]
        result["country"] = result_country
        result["products"] = result_product
        result["equity"] = result_equity
        result["red_flag"] = result_red_flag
        return JsonResponse(result, safe=False)
