from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period


class RedFlagSummaryView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        if country:
            filter_args["country__country_code_alpha_2"] = country
        filter_args["red_flag__isnull"] = False
        result = []
        equity_summary = (
            Tender.objects.filter(**filter_args)
            .annotate(month=TruncMonth("contract_date"))
            .values("month", "red_flag", "red_flag__title", "red_flag__implemented")
            .annotate(
                total=Count("id"),
                local=Sum("contract_value_local"),
                usd=Sum("contract_value_usd"),
            )
            .order_by("-month")
        )
        for detail in equity_summary:
            if detail["red_flag__implemented"]:
                data = {
                    "amount_local": detail["local"],
                    "amount_usd": detail["usd"],
                    "red_flag": detail["red_flag__title"],
                    "red_flag_id": detail["red_flag"],
                    "month": detail["month"],
                    "tender_count": detail["total"],
                }
                result.append(data)
        return JsonResponse(result, safe=False)
