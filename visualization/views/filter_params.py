from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Buyer, Country, GoodsServicesCategory, Supplier
from helpers.general import page_expire_period


class FilterParams(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request, *args, **kwargs):
        try:
            buyers = Buyer.objects.values("id", "buyer_name")
            suppliers = Supplier.objects.values("id", "supplier_name")
            countries = Country.objects.values("id", "country_code", "name")
            products = GoodsServicesCategory.objects.values("id", "category_name")

            result_buyer = []
            result_supplier = []
            result_country = []
            result_product = []
            result = {}

            if buyers:
                result_buyer = [{"id": buyer["id"], "name": buyer["buyer_name"]} for buyer in buyers]
            if suppliers:
                result_supplier = [{"id": supplier["id"], "name": supplier["supplier_name"]} for supplier in suppliers]

            if countries:
                result_country = [
                    {"id": country["id"], "code": country["country_code"], "name": country["name"]}
                    for country in countries
                ]

            if products:
                result_product = [{"id": product["id"], "name": product["category_name"]} for product in products]

            result = {
                "buyer": result_buyer,
                "contracts": {
                    "method": [
                        {"label": "Direct", "value": "direct"},
                        {"label": "Limited", "value": "limited"},
                        {"label": "Open", "value": "open"},
                        {"label": "Other", "value": "other"},
                        {"label": "Selective", "value": "selective"},
                    ],
                    "status": [
                        {"label": "Active", "value": "active"},
                        {"label": "Cancelled", "value": "cancelled"},
                        {"label": "Completed", "value": "completed"},
                        {"label": "Other", "value": "other"},
                    ],
                },
                "country": result_country,
                "product": result_product,
                "supplier": result_supplier,
            }

            return JsonResponse(result, safe=False)

        except Exception:
            return JsonResponse([{"error": "No buyer and supplier data available"}], safe=False)
