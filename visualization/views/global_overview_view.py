import dateutil.relativedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, Tender
from helpers.general import page_expire_period


class GlobalOverview(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        temp = {}
        tender_temp = {}
        data = []
        count = (
            Tender.objects.annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(
                total_contract=Count("id"),
                total_amount=Sum("contract_value_usd"),
            )
            .order_by("month")
        )
        countries = Country.objects.all().exclude(country_code_alpha_2="gl")
        for item in count:
            result = {}
            end_date = item["month"] + dateutil.relativedelta.relativedelta(months=1)
            start_date = item["month"]
            result["details"] = []
            result["month"] = str(start_date.year) + "-" + str(start_date.month)
            for country in countries:
                b = {}
                tender = Tender.objects.filter(
                    country__country_code_alpha_2=country.country_code_alpha_2,
                    contract_date__gte=start_date,
                    contract_date__lte=end_date,
                ).aggregate(Sum("contract_value_usd"), Count("id"))
                b["country"] = country.name
                b["country_code"] = country.country_code_alpha_2
                b["country_continent"] = country.continent
                if tender["contract_value_usd__sum"] is None:
                    tender_val = 0
                else:
                    tender_val = tender["contract_value_usd__sum"]
                if tender["id__count"] is None:
                    contract_val = 0
                else:
                    contract_val = tender["id__count"]
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
                    cum_value = current_val + contract_val
                    tender_temp[country.name] = cum_value
                    b["tender_count"] = cum_value
                else:
                    tender_temp[country.name] = contract_val
                    b["tender_count"] = contract_val
                result["details"].append(b)
            data.append(result)
        return JsonResponse({"result": data})
