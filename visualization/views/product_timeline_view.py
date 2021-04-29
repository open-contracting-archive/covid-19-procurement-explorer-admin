from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class ProductTimelineView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        supplier = self.request.GET.get("supplier")
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)
        result = []
        if country:
            try:
                country_instance = Country.objects.get(country_code_alpha_2=country)
                currency = country_instance.currency
                filter_args["country"] = country_instance
                tenders_assigned = (
                    Tender.objects.filter(**filter_args)
                    .exclude(goods_services__goods_services_category=None)
                    .annotate(month=TruncMonth("contract_date"))
                    .values(
                        "month",
                        "goods_services__goods_services_category__category_name",
                        "goods_services__goods_services_category__id",
                    )
                    .annotate(
                        count=Count("id"),
                        local=Sum("goods_services__contract_value_local"),
                        usd=Sum("goods_services__contract_value_usd"),
                    )
                    .order_by("-month")
                )
                for tender in tenders_assigned:
                    data = {}
                    data["amount_local"] = tender["local"]
                    data["amount_usd"] = tender["usd"]
                    data["date"] = tender["month"]
                    data["local_currency_code"] = currency
                    data["product_id"] = tender["goods_services__goods_services_category__id"]
                    data["product_name"] = tender["goods_services__goods_services_category__category_name"]
                    data["tender_count"] = tender["count"]
                    result.append(data)
                return JsonResponse(result, safe=False)
            except Exception:
                return JsonResponse([{"error": "Invalid country_code"}], safe=False)
        else:
            tenders_assigned = (
                Tender.objects.filter(**filter_args)
                .exclude(goods_services__goods_services_category=None)
                .annotate(month=TruncMonth("contract_date"))
                .values(
                    "month",
                    "goods_services__goods_services_category__category_name",
                    "goods_services__goods_services_category__id",
                )
                .annotate(
                    count=Count("id"),
                    local=Sum("goods_services__contract_value_local"),
                    usd=Sum("goods_services__contract_value_usd"),
                )
                .order_by("-month")
            )
            try:
                for tender in tenders_assigned:
                    data = {}
                    data["amount_local"] = tender["local"]
                    data["amount_usd"] = tender["usd"]
                    data["date"] = tender["month"]
                    data["local_currency_code"] = "USD"
                    data["product_id"] = tender["goods_services__goods_services_category__id"]
                    data["product_name"] = tender["goods_services__goods_services_category__category_name"]
                    data["tender_count"] = tender["count"]
                    result.append(data)
                return JsonResponse(result, safe=False)
            except Exception:
                return JsonResponse([{"error": "Invalid country_code"}], safe=False)
            return JsonResponse(data, safe=False)
