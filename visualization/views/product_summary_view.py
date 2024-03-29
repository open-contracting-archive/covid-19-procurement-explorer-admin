from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, Tender
from helpers.general import page_expire_period


class ProductSummaryView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        country_code = self.request.GET.get("country", None)
        currency = "USD"
        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code
            instance = Country.objects.get(country_code_alpha_2=country_code)
            currency = instance.currency
        result = []
        tenders_assigned = (
            Tender.objects.filter(**filter_args)
            .exclude(goods_services__goods_services_category=None)
            .annotate(category=Count("goods_services__goods_services_category__category_name"))
            .values(
                "goods_services__goods_services_category__category_name", "goods_services__goods_services_category__id"
            )
            .annotate(
                count=Count("id"),
                local=Sum("contract_value_local"),
                usd=Sum("contract_value_usd"),
            )
        )
        for tender in tenders_assigned:
            data = {
                "amount_local": tender["local"],
                "amount_usd": tender["usd"],
                "local_currency_code": currency,
                "product_id": tender["goods_services__goods_services_category__id"],
                "product_name": tender["goods_services__goods_services_category__category_name"],
                "tender_count": tender["count"],
            }
            result.append(data)
        return JsonResponse(result, safe=False)
