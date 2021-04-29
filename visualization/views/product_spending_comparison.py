from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period


class ProductSpendingComparison(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        product = self.request.GET.get("product", None)
        if product:
            filter_args["goods_services__goods_services_category__id"] = product
            amount_usd_local = (
                Tender.objects.filter(**filter_args)
                .annotate(month=TruncMonth("contract_date"))
                .values(
                    "country__country_code_alpha_2",
                    "country__currency",
                    "month",
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                )
                .annotate(
                    usd=Sum("goods_services__contract_value_usd"), local=Sum("goods_services__contract_value_usd")
                )
                .order_by("-month")
            )
            count = (
                Tender.objects.filter(**filter_args)
                .annotate(month=TruncMonth("contract_date"))
                .values(
                    "country__country_code_alpha_2",
                    "country__currency",
                    "month",
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                )
                .annotate(count=Count("id"))
                .order_by("-month")
            )
            result = [
                {
                    "amount_local": i["local"],
                    "amount_usd": i["usd"],
                    "country_code": i["country__country_code_alpha_2"],
                    "currency": i["country__currency"],
                    "month": i["month"].strftime("%Y-%m"),
                    "product_id": i["goods_services__goods_services_category__id"],
                    "product_name": i["goods_services__goods_services_category__category_name"],
                }
                for i in amount_usd_local
            ]
            for i in range(len(count)):
                result[i]["tender_count"] = count[i]["count"]
            return JsonResponse(result, safe=False)
        else:
            amount_usd_local = (
                Tender.objects.annotate(month=TruncMonth("contract_date"))
                .values(
                    "country__country_code_alpha_2",
                    "country__currency",
                    "month",
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                )
                .annotate(
                    usd=Sum("goods_services__contract_value_usd"), local=Sum("goods_services__contract_value_usd")
                )
                .order_by("-month")
            )
            count = (
                Tender.objects.annotate(month=TruncMonth("contract_date"))
                .values(
                    "country__country_code_alpha_2",
                    "country__currency",
                    "month",
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                )
                .annotate(count=Count("id"))
                .order_by("-month")
            )
            result = [
                {
                    "amount_local": i["local"],
                    "amount_usd": i["usd"],
                    "country_code": i["country__country_code_alpha_2"],
                    "currency": i["country__currency"],
                    "month": i["month"].strftime("%Y-%m"),
                    "product_id": i["goods_services__goods_services_category__id"],
                    "product_name": i["goods_services__goods_services_category__category_name"],
                }
                for i in amount_usd_local
            ]
            for i in range(len(count)):
                result[i]["tender_count"] = count[i]["count"]
            return JsonResponse(result, safe=False)
