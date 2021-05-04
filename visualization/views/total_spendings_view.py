from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class TotalSpendingsView(APIView):
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

        total_country_tender_amount = (
            Tender.objects.filter(**filter_args)
            .exclude(**exclude_args)
            .aggregate(usd=Sum("contract_value_usd"), local=Sum("contract_value_local"))
        )

        bar_chart = (
            Tender.objects.filter(**filter_args)
            .exclude(**exclude_args)
            .values("procurement_procedure")
            .annotate(usd=Sum("contract_value_usd"), local=Sum("contract_value_local"))
        )
        selective_sum_local = 0
        limited_sum_local = 0
        open_sum_local = 0
        direct_sum_local = 0
        limited_total = 0
        open_total = 0
        selective_total = 0
        direct_total = 0
        not_identified_total = 0
        not_identified_sum_local = 0

        for i in bar_chart:
            if i["procurement_procedure"] == "selective":
                selective_total = i["usd"]
                selective_sum_local = i["local"]
            elif i["procurement_procedure"] == "limited":
                limited_total = i["usd"]
                limited_sum_local = i["local"]
            elif i["procurement_procedure"] == "open":
                open_total = i["usd"]
                open_sum_local = i["local"]
            elif i["procurement_procedure"] == "direct":
                direct_total = i["usd"]
                direct_sum_local = i["local"]
            elif i["procurement_procedure"] == "not_identified":
                not_identified_total = i["usd"]
                not_identified_sum_local = i["local"]

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
                "total": total_country_tender_amount["usd"],
                "line_chart": line_chart_list,
                "bar_chart": [
                    {"method": "open", "value": open_total},
                    {"method": "limited", "value": limited_total},
                    {"method": "selective", "value": selective_total},
                    {"method": "direct", "value": direct_total},
                    {"method": "not_identified", "value": not_identified_total},
                ],
            },
            "local": {
                "total": total_country_tender_amount["local"],
                "line_chart": line_chart_local_list,
                "bar_chart": [
                    {"method": "open", "value": open_sum_local},
                    {"method": "limited", "value": limited_sum_local},
                    {"method": "selective", "value": selective_sum_local},
                    {"method": "direct", "value": direct_sum_local},
                    {"method": "not_identified", "value": not_identified_sum_local},
                ],
            },
        }
        return JsonResponse(result)
