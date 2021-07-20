from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class TotalContractsView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        """
        Return a list of all contracts.
        """
        # Calculating total tender
        country_code = self.request.GET.get("country", None)
        buyer_id = self.request.GET.get("buyer")
        supplier_id = self.request.GET.get("supplier")

        total_contract = 0
        bar_chart_list = []
        filter_args = {}
        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code
        if buyer_id:
            filter_args = add_filter_args("buyer", buyer_id, filter_args)
        if supplier_id:
            filter_args = add_filter_args("supplier", supplier_id, filter_args)

        bar_chart = (
            Tender.objects.filter(**filter_args)
            .values("procurement_procedure")
            .annotate(count=Count("procurement_procedure"), total_contract=Count("id"))
        )
        for i in bar_chart:
            total_contract += i["total_contract"]
            bar_chart_list.append({"method": i["procurement_procedure"], "value": i["count"]})

        line_chart = (
            Tender.objects.filter(**filter_args)
            .annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("-month")
        )
        line_chart_list = [{"date": i["month"], "value": i["total"]} for i in line_chart]
        result = {
            "total": total_contract,
            "line_chart": line_chart_list,
            "bar_chart": bar_chart_list,
        }
        return JsonResponse(result)
