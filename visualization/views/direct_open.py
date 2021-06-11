from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


def procurement_procedure_amount(**filter_args):
    result = (
        Tender.objects.filter(procurement_procedure__in=["open", "direct", "not_identified"], **filter_args)
        .values("procurement_procedure")
        .annotate(
            count=Count("id"),
            usd=Sum("contract_value_usd"),
            local=Sum("contract_value_local"),
        )
    )
    return result


class DirectOpen(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        country_code = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        supplier = self.request.GET.get("supplier")
        filter_args = {}
        country_currency = ""

        results = {}

        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
            results = procurement_procedure_amount(**filter_args)

        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)
            results = procurement_procedure_amount(**filter_args)

        if country_code:
            country_code = str(country_code).upper()
            country_obj = Country.objects.get(country_code_alpha_2=country_code)
            country_currency = country_obj.currency

            filter_args = add_filter_args("country__country_code_alpha_2", country_code, filter_args, append_only=True)
            results = procurement_procedure_amount(**filter_args)

        if not country_code and not supplier and not buyer:
            results = procurement_procedure_amount(**filter_args)

        response = []

        for result in results:
            response.append(
                {
                    "amount_local": result["local"] if result["local"] else 0,
                    "amount_usd": result["usd"] if result["usd"] else 0,
                    "tender_count": result["count"],
                    "local_currency_code": country_currency,
                    "status": result["procurement_procedure"] if result["procurement_procedure"] else "",
                }
            )

        return JsonResponse(response, safe=False)
