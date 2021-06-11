from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period


class EquitySummaryView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {"equity_category__isnull": False}
        country_code = self.request.GET.get("country", None)

        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code

        result = []
        equity_summary = (
            Tender.objects.filter(**filter_args)
            .annotate(month=TruncMonth("contract_date"))
            .values("month", "equity_category", "equity_category__category_name")
            .annotate(
                total=Count("id"),
                local=Sum("contract_value_local"),
                usd=Sum("contract_value_usd"),
            )
            .order_by("-month")
        )
        for detail in equity_summary:
            data = {
                "amount_local": detail["local"],
                "amount_usd": detail["usd"],
                "equity": detail["equity_category__category_name"],
                "equity_category_id": detail["equity_category"],
                "month": detail["month"],
                "tender_count": detail["total"],
            }
            result.append(data)
        return JsonResponse(result, safe=False)
