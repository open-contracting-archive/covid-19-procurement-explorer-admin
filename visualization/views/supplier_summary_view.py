import datetime

import dateutil.relativedelta
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period


class SupplierSummaryView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        result = {}
        trend = []
        current_time = datetime.datetime.now()
        previous_month_date = current_time - dateutil.relativedelta.relativedelta(months=-1)
        previous_month = previous_month_date.replace(day=1).date()
        if country:
            filter_args["country__country_code_alpha_2"] = country
        supplier_details = (
            Tender.objects.filter(**filter_args)
            .exclude(supplier__isnull=True)
            .annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(count=Count("supplier_id", distinct=True))
            .order_by("-month")
        )
        totals = (
            Tender.objects.filter(**filter_args)
            .exclude(supplier__isnull=True)
            .values("supplier")
            .distinct()
            .aggregate(total=Count("supplier"))
        )
        for details in supplier_details:
            data = {"supplier_count": details["count"], "month": details["month"]}
            trend.append(data)
        try:
            dates_in_details = [i["month"] for i in supplier_details]
            final_current_month_count = [
                supplier_details[0]["count"] if current_time.replace(day=1).date() in dates_in_details else 0
            ]
            final_previous_month_count = [supplier_details[1]["count"] if previous_month in dates_in_details else 0]
            percentage = round(
                ((final_current_month_count[0] - final_previous_month_count[0]) / final_previous_month_count[0]) * 100
            )
        except Exception:
            percentage = 0
        result["total"] = totals["total"]
        result["percentage"] = percentage
        result["trend"] = trend
        return JsonResponse(result, safe=False)
