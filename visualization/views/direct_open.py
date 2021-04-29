from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class DirectOpen(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        supplier = self.request.GET.get("supplier")
        filter_args = {}
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)

        if country:
            amount_direct = (
                Tender.objects.filter(country__country_code_alpha_2=country, procurement_procedure="direct")
                .values("country__currency")
                .annotate(
                    count=Count("contract_id", distinct=True),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )
            amount_open = (
                Tender.objects.filter(country__country_code_alpha_2=country, procurement_procedure="open")
                .values("country__currency")
                .annotate(
                    count=Count("contract_id", distinct=True),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )

            amount_not_identified = (
                Tender.objects.filter(country__country_code_alpha_2=country, procurement_procedure="not_identified")
                .values("country__currency")
                .annotate(
                    count=Count("contract_id", distinct=True),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )
        elif buyer or supplier:
            amount_direct = (
                Tender.objects.filter(**filter_args, procurement_procedure="direct")
                .values("procurement_procedure")
                .annotate(
                    count=Count("contract_id", distinct=True),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )
            amount_open = (
                Tender.objects.filter(**filter_args, procurement_procedure="open")
                .values("procurement_procedure")
                .annotate(
                    count=Count("contract_id", distinct=True),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )
            amount_not_identified = (
                Tender.objects.filter(**filter_args, procurement_procedure="not_identified")
                .values("procurement_procedure")
                .annotate(
                    count=Count("contract_id", distinct=True),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )
        else:
            amount_direct = (
                Tender.objects.filter(procurement_procedure="direct")
                .values("procurement_procedure")
                .annotate(
                    count=Count("contract_id", distinct=True),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )
            amount_open = (
                Tender.objects.filter(procurement_procedure="open")
                .values("procurement_procedure")
                .annotate(
                    count=Count("contract_id", distinct=True),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )
            amount_not_identified = (
                Tender.objects.filter(procurement_procedure="not_identified")
                .values("procurement_procedure")
                .annotate(
                    count=Count("contract_id", distinct=True),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )

        country_currency = []
        if country:
            country_obj = Country.objects.filter(name=country)
            if country_obj:
                country_currency = country_obj.currency
        if amount_direct:
            for i in amount_direct:
                result_direct = {
                    "amount_local": i["local"] if i["local"] else 0,
                    "amount_usd": i["usd"] if i["usd"] else 0,
                    "tender_count": i["count"],
                    "local_currency_code": i["country__currency"] if "country__currency" in i else "",
                    "procedure": "direct",
                }
        else:
            result_direct = {
                "amount_local": 0,
                "amount_usd": 0,
                "tender_count": 0,
                "local_currency_code": country_currency,
                "procedure": "direct",
            }

        if amount_open:
            for i in amount_open:
                result_open = {
                    "amount_local": i["local"] if i["local"] else 0,
                    "amount_usd": i["usd"] if i["usd"] else 0,
                    "tender_count": i["count"],
                    "local_currency_code": i["country__currency"] if "country__currency" in i else "",
                    "procedure": "open",
                }
        else:
            result_open = {
                "amount_local": 0,
                "amount_usd": 0,
                "tender_count": 0,
                "local_currency_code": country_currency,
                "procedure": "open",
            }

        if amount_not_identified:
            for i in amount_not_identified:
                result_not_identified = {
                    "amount_local": i["local"] if i["local"] else 0,
                    "amount_usd": i["usd"] if i["usd"] else 0,
                    "tender_count": i["count"],
                    "local_currency_code": i["country__currency"] if "country__currency" in i else "",
                    "procedure": "not_identified",
                }
        else:
            result_not_identified = {
                "amount_local": 0,
                "amount_usd": 0,
                "tender_count": 0,
                "local_currency_code": country_currency,
                "procedure": "not_identified",
            }

        result = [result_direct, result_open, result_not_identified]

        return JsonResponse(result, safe=False)
