from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class TotalSpendingView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        """
        Return a list of all contracts.
        """

        # Calculating total tender
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        supplier = self.request.GET.get("supplier")

        filter_args = {}
        exclude_args = {"status": "canceled"}
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)

        bar_chart = (
            Tender.objects.filter(**filter_args)
            .exclude(**exclude_args)
            .values("procurement_procedure")
            .annotate(usd=Sum("contract_value_usd"), local=Sum("contract_value_local"))
        )

        total_country_usd_sum = 0
        total_country_local_sum = 0
        bar_chart_usd = []
        bar_chart_local = []

        for i in bar_chart:
            total_country_usd_sum += i["usd"] if i["usd"] else 0
            total_country_local_sum += i["local"] if i["local"] else 0
            bar_chart_usd.append({"method": i["procurement_procedure"], "value": i["usd"]})

            bar_chart_local.append({"method": i["procurement_procedure"], "value": i["local"]})

        line_chart = (
            Tender.objects.filter(**filter_args)
            .exclude(**exclude_args)
            .annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(usd=Sum("contract_value_usd"), local=Sum("contract_value_local"))
            .order_by("-month")
        )
        line_chart_local_list = [{"date": i["month"], "value": i["local"]} for i in line_chart]
        line_chart_list = [{"date": i["month"], "value": i["usd"]} for i in line_chart]

        result = {
            "usd": {
                "total": total_country_usd_sum,
                "line_chart": line_chart_list,
                "bar_chart": bar_chart_usd,
            },
            "local": {
                "total": total_country_local_sum,
                "line_chart": line_chart_local_list,
                "bar_chart": bar_chart_local,
            },
        }
        return JsonResponse(result)
