from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import GoodsServicesCategory, Tender
from visualization.helpers.general import page_expire_period


class ProductSpendingComparison(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        product_id = self.request.GET.get("product", None)

        if product_id:
            product_category = GoodsServicesCategory.objects.filter(id=product_id).first()
            filter_args["goods_services__goods_services_category__id"] = product_id
            month_wise_data = (
                Tender.objects.filter(**filter_args)
                .annotate(month=TruncMonth("contract_date"))
                .values(
                    "country__country_code_alpha_2",
                    "country__currency",
                    "month",
                )
                .annotate(
                    usd=Sum("contract_value_usd"), local=Sum("contract_value_local"), count=Count("id", distinct=True)
                )
                .order_by("-month")
            )
            result = [
                {
                    "amount_usd": i["usd"],
                    "amount_local": i["local"],
                    "tender_count": i["count"],
                    "country_code": i["country__country_code_alpha_2"],
                    "currency": i["country__currency"],
                    "month": i["month"].strftime("%Y-%m"),
                    "product_id": product_category.id,
                    "product_name": product_category.category_name,
                }
                for i in month_wise_data
            ]
            return JsonResponse(result, safe=False)
        else:
            return JsonResponse([], safe=False)
