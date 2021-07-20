import dateutil.relativedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, Tender
from helpers.general import page_expire_period


class BuyerTrendView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        temp = {}
        tender_temp = {}
        data = []
        monthly_contract = (
            Tender.objects.annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(total_buyer_count=Count("buyer__id", distinct=True), sum=Sum("contract_value_usd"))
            .order_by("month")
        )
        countries = Country.objects.exclude(country_code_alpha_2="gl").all()
        for contract in monthly_contract:
            end_date = contract["month"] + dateutil.relativedelta.relativedelta(months=1)
            start_date = contract["month"]
            result = {"details": [], "month": str(start_date.year) + "-" + str(start_date.month)}
            for country in countries:
                tender = Tender.objects.filter(
                    country__country_code_alpha_2=country.country_code_alpha_2,
                    contract_date__gte=start_date,
                    contract_date__lte=end_date,
                ).aggregate(
                    total_buyer_count=Count("buyer__id", distinct=True),
                    amount_usd=Sum("contract_value_usd"),
                )

                b = {
                    "country": country.name,
                    "country_code": country.country_code_alpha_2,
                    "country_continent": country.continent,
                }
                buyer_count = tender["total_buyer_count"]

                tender_val = 0
                if tender["amount_usd"] is not None:
                    tender_val = tender["amount_usd"]

                buyer_val = 0
                if buyer_count is not None:
                    buyer_val = buyer_count

                if bool(temp) and country.name in temp.keys():
                    current_val = temp[country.name]
                    cum_value = current_val + tender_val
                    temp[country.name] = cum_value
                    b["amount_usd"] = cum_value
                else:
                    temp[country.name] = tender_val
                    b["amount_usd"] = tender_val

                if bool(tender_temp) and country.name in tender_temp.keys():
                    current_val = tender_temp[country.name]
                    cum_value = current_val + buyer_val
                    tender_temp[country.name] = cum_value
                    b["buyer_count"] = cum_value
                else:
                    tender_temp[country.name] = buyer_val
                    b["buyer_count"] = buyer_val

                result["details"].append(b)
            data.append(result)
        return JsonResponse({"result": data})
