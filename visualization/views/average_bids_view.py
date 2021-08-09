from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class AverageBidsView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        """
        Returns average bids for contracts
        """
        country_code = self.request.GET.get("country", None)
        buyer_id = self.request.GET.get("buyer")

        filter_args = {}
        filter_args["no_of_bidders__gte"] = 1
        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code
        if buyer_id:
            filter_args = add_filter_args("buyer", buyer_id, filter_args)

        # Month wise average of number of bids for contracts
        monthwise_data = (
            Tender.objects.filter(**filter_args)
            .annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(count=Count("id"), sum=Sum("no_of_bidders"))
            .order_by("-month")
        )
        final_line_chart_data = [
            {
                "date": monthwise_data[i]["month"],
                "value": round(monthwise_data[i]["sum"] / monthwise_data[i]["count"], 1)
                if monthwise_data[i]["sum"]
                else 0,
            }
            for i in range(len(monthwise_data))
        ]

        # Difference percentage calculation

        result = {
            "average": round(sum(item["value"] for item in final_line_chart_data) / len(final_line_chart_data), 1)
            if len(final_line_chart_data) > 0
            else 0,
            "line_chart": final_line_chart_data,
        }
        return JsonResponse(result)
