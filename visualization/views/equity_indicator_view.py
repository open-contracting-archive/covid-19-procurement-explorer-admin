from django.db.models import Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, Tender
from helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class EquityIndicatorView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        country_code = self.request.GET.get("country", None)
        buyer_id = self.request.GET.get("buyer")
        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code
        if buyer_id:
            filter_args = add_filter_args("buyer", buyer_id, filter_args)
        if country_code:
            try:
                country_instance = Country.objects.get(country_code_alpha_2=country_code)
                filter_args["country"] = country_instance
                tenders_assigned = (
                    Tender.objects.filter(**filter_args)
                    .exclude(equity_category=None)
                    .aggregate(
                        total_usd=Sum("contract_value_usd"),
                        total_local=Sum("contract_value_local"),
                    )
                )
                assigned_count = Tender.objects.filter(**filter_args).exclude(equity_category=None).count()
                filter_args["equity_category"] = None
                tenders_unassigned = Tender.objects.filter(**filter_args).aggregate(
                    total_usd=Sum("contract_value_usd"),
                    total_local=Sum("contract_value_local"),
                )
                unassigned_count = Tender.objects.filter(**filter_args).count()
                data = [
                    {
                        "amount_local": tenders_assigned["total_local"],
                        "amount_usd": tenders_assigned["total_usd"],
                        "tender_count": assigned_count,
                        "local_currency_code": country_instance.currency,
                        "type": "assigned",
                    },
                    {
                        "amount_local": tenders_unassigned["total_local"],
                        "amount_usd": tenders_unassigned["total_usd"],
                        "tender_count": unassigned_count,
                        "local_currency_code": country_instance.currency,
                        "type": "unassigned",
                    },
                ]
                return JsonResponse(data, safe=False)
            except Exception:
                return JsonResponse([{"error": "Invalid country_code"}], safe=False)
        else:
            tenders_assigned = (
                Tender.objects.filter(**filter_args)
                .exclude(equity_category=None)
                .aggregate(
                    total_usd=Sum("contract_value_usd"),
                    total_local=Sum("contract_value_local"),
                )
            )
            assigned_count = Tender.objects.filter(**filter_args).exclude(equity_category=None).count()
            filter_args["equity_category"] = None
            tenders_unassigned = Tender.objects.filter(**filter_args).aggregate(
                total_usd=Sum("contract_value_usd"),
                total_local=Sum("contract_value_local"),
            )
            unassigned_count = Tender.objects.filter(**filter_args).count()
            data = [
                {
                    "amount_local": tenders_assigned["total_local"],
                    "amount_usd": tenders_assigned["total_usd"],
                    "tender_count": assigned_count,
                    "local_currency_code": "USD",
                    "type": "assigned",
                },
                {
                    "amount_local": tenders_unassigned["total_local"],
                    "amount_usd": tenders_unassigned["total_usd"],
                    "tender_count": unassigned_count,
                    "local_currency_code": "USD",
                    "type": "unassigned",
                },
            ]
            return JsonResponse(data, safe=False)
