import datetime

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import CovidMonthlyActiveCases, Tender
from visualization.helpers.general import page_expire_period


class QuantityCorrelation(APIView):
    today = datetime.datetime.now()

    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        country = self.request.GET.get("country", None)
        filter_args = {}
        if country:
            filter_args["country__country_code_alpha_2"] = country

        contracts_quantity = (
            Tender.objects.filter(**filter_args)
            .annotate(month=TruncMonth("contract_date"))
            .values("month", "country__currency")
            .annotate(
                count=Count("id"),
                usd=Sum("contract_value_usd"),
                local=Sum("contract_value_local"),
            )
            .order_by("-month")
        )

        contracts_quantity_list = []

        for i in contracts_quantity:
            active_case = CovidMonthlyActiveCases.objects.filter(
                **filter_args, covid_data_date__year=i["month"].year, covid_data_date__month=i["month"].month
            ).values("active_cases_count", "death_count")
            active_case_count = 0
            death_count = 0
            try:
                for j in active_case:
                    if j["active_cases_count"] and j["death_count"]:
                        active_case_count += j["active_cases_count"]
                        death_count += j["death_count"]
            except Exception:
                pass

            contracts_quantity_list.append(
                {
                    "active_cases": active_case_count,
                    "death_cases": death_count,
                    "amount_local": i["local"] if "local" in i else "",
                    "amount_usd": i["usd"],
                    "local_currency_code": i["country__currency"] if "country__currency" in i else "",
                    "month": i["month"],
                    "tender_count": i["count"],
                }
            )

        return JsonResponse(contracts_quantity_list, safe=False)
