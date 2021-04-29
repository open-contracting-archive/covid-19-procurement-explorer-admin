from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
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
        status = ["active", "completed", "cancelled", "not_identified"]
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")

        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)

        # Status code wise grouped sum of contract value
        contract_value_local_sum = (
            Tender.objects.filter(**filter_args)
            .values("status")
            .annotate(sum=Sum("goods_services__contract_value_local"))
        )
        contract_value_usd_sum = (
            Tender.objects.filter(**filter_args)
            .values("status")
            .annotate(sum=Sum("goods_services__contract_value_usd"))
        )

        # Status code wise grouped total number of contracts
        grouped_contract_no = Tender.objects.filter(**filter_args).values("status").annotate(count=Count("id"))

        if country:
            try:
                country_res = Country.objects.get(country_code_alpha_2=country)
                currency_code = country_res.currency
            except Exception as e:
                print(e)

        status_in_result = [i["status"] for i in contract_value_local_sum]
        for i in range(len(status)):
            if status[i] in status_in_result:
                result.append(
                    {
                        "amount_local": [
                            each["sum"] if each["sum"] else 0
                            for each in contract_value_local_sum
                            if status[i] == each["status"]
                        ][0],
                        "amount_usd": [
                            each["sum"] if each["sum"] else 0
                            for each in contract_value_usd_sum
                            if status[i] == each["status"]
                        ][0],
                        "tender_count": [
                            each["count"] if each["count"] else 0
                            for each in grouped_contract_no
                            if status[i] == each["status"]
                        ][0],
                        "local_currency_code": currency_code,
                        "status": status[i],
                    }
                )
            else:
                result.append(
                    {
                        "amount_local": 0,
                        "amount_usd": 0,
                        "tender_count": 0,
                        "local_currency_code": currency_code,
                        "status": status[i],
                    }
                )

        return JsonResponse(result, safe=False)
