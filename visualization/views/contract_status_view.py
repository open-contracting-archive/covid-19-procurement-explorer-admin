from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status as status_code
from rest_framework.views import APIView

from country.models import Country, Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class ContractStatusView(APIView):
    """
    Returns status wise grouped info about contracts
    """

    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        result = list()
        currency_code = ""

        country_code = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")

        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code

        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)

        if country_code:
            try:
                country_res = Country.objects.get(country_code_alpha_2=country_code)
                currency_code = country_res.currency
            except Exception as e:
                return JsonResponse({"error": str(e)}, safe=False, status=status_code.HTTP_500_INTERNAL_SERVER_ERROR)

        status_query_set = (
            Tender.objects.filter(**filter_args)
            .values("status")
            .annotate(
                amount_usd=Sum("contract_value_usd"),
                amount_local=Sum("contract_value_local"),
                tender_count=Count("id"),
            )
        )

        for status in status_query_set:
            data = {
                "amount_local": status["amount_local"],
                "amount_usd": status["amount_usd"],
                "tender_count": status["tender_count"],
                "local_currency_code": currency_code,
                "status": status["status"],
            }

            result.append(data)

        return JsonResponse(result, safe=False)
