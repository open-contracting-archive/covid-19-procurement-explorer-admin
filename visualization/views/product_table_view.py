from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period


class ProductTableView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        if country:
            filter_args["country__country_code_alpha_2"] = country
        filter_args["goods_services__goods_services_category__isnull"] = False
        result = []
        product_tables = (
            Tender.objects.filter(**filter_args)
            .values(
                "goods_services__goods_services_category__category_name", "goods_services__goods_services_category__id"
            )
            .annotate(
                total=Count("id", distinct=True),
                local=Sum("goods_services__contract_value_local"),
                usd=Sum("goods_services__contract_value_usd"),
                buyer=Count("buyer", distinct=True),
                supplier=Count("supplier", distinct=True),
            )
        )
        for product in product_tables:
            data = {}
            data["amount_local"] = product["local"]
            data["amount_usd"] = product["usd"]
            data["product_id"] = product["goods_services__goods_services_category__id"]
            data["product_name"] = product["goods_services__goods_services_category__category_name"]
            data["buyer_count"] = product["buyer"]
            data["supplier_count"] = product["supplier"]
            data["tender_count"] = product["total"]
            result.append(data)
        return JsonResponse(result, safe=False)
