from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class TotalContractsView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        """
        Return a list of all contracts.
        """
        # Calculating total tender
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        supplier = self.request.GET.get("supplier")

        open_count = 0
        selective_count = 0
        direct_count = 0
        limited_count = 0
        not_identified_count = 0
        filter_args = {}
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)

        total_country_tender = Tender.objects.filter(**filter_args).count()
        bar_chart = (
            Tender.objects.filter(**filter_args)
            .values("procurement_procedure")
            .annotate(count=Count("procurement_procedure"))
        )
        for i in bar_chart:
            if i["procurement_procedure"] == "selective":
                selective_count = i["count"]
            elif i["procurement_procedure"] == "limited":
                limited_count = i["count"]
            elif i["procurement_procedure"] == "open":
                open_count = i["count"]
            elif i["procurement_procedure"] == "direct":
                direct_count = i["count"]
            elif i["procurement_procedure"] == "not_identified":
                not_identified_count = i["count"]

        line_chart = (
            Tender.objects.filter(**filter_args)
            .annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("-month")
        )
        line_chart_list = [{"date": i["month"], "value": i["total"]} for i in line_chart]
        result = {
            "total": total_country_tender,
            "line_chart": line_chart_list,
            "bar_chart": [
                {"method": "open", "value": open_count},
                {"method": "limited", "value": limited_count},
                {"method": "selective", "value": selective_count},
                {"method": "direct", "value": direct_count},
                {"method": "not_identified", "value": not_identified_count},
            ],
        }
        return JsonResponse(result)
