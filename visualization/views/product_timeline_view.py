from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class ProductTimelineView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        country_code = self.request.GET.get("country", None)
        buyer_id = self.request.GET.get("buyer")
        supplier_id = self.request.GET.get("supplier")
        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code
        if buyer_id:
            filter_args = add_filter_args("buyer", buyer_id, filter_args)
        if supplier_id:
            filter_args = add_filter_args("supplier", supplier_id, filter_args)
        result = []
        try:
            tenders_assigned = (
                Tender.objects.filter(**filter_args)
                .exclude(goods_services__goods_services_category=None)
                .annotate(month=TruncMonth("contract_date"))
                .values(
                    "month",
                    "goods_services__goods_services_category__category_name",
                    "goods_services__goods_services_category__id",
                    "country__currency",
                )
                .annotate(
                    count=Count("id"),
                    local=Sum("contract_value_local"),
                    usd=Sum("contract_value_usd"),
                )
                .order_by("-month")
            )
            for tender in tenders_assigned:
                data = {
                    "amount_local": tender["local"],
                    "amount_usd": tender["usd"],
                    "date": tender["month"],
                    "local_currency_code": tender["country__currency"],
                    "product_id": tender["goods_services__goods_services_category__id"],
                    "product_name": tender["goods_services__goods_services_category__category_name"],
                    "tender_count": tender["count"],
                }
                result.append(data)
            return JsonResponse(result, safe=False)
        except Exception:
            return JsonResponse([{"error": "Invalid country_code"}], safe=False)
