import dateutil.relativedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, Tender
from visualization.helpers.general import page_expire_period


class DirectOpenContractTrendView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        temp = {}
        tender_temp = {}
        data = []
        count = (
            Tender.objects.annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(total_contract=Count("id"), total_amount=Sum("contract_value_usd"))
            .order_by("month")
        )
        countries = Country.objects.all().exclude(country_code_alpha_2="gl")
        for i in count:
            result = {}
            end_date = i["month"] + dateutil.relativedelta.relativedelta(months=1)
            start_date = i["month"]
            result["details"] = []
            result["month"] = str(start_date.year) + "-" + str(start_date.month)
            for j in countries:
                b = {}
                contracts = ["direct", "Direct", "open", "Open"]
                tender_count = Tender.objects.filter(
                    country__country_code_alpha_2=j.country_code_alpha_2,
                    contract_date__gte=start_date,
                    contract_date__lte=end_date,
                    procurement_procedure__in=contracts,
                ).count()
                tender = Tender.objects.filter(
                    country__country_code_alpha_2=j.country_code_alpha_2,
                    contract_date__gte=start_date,
                    contract_date__lte=end_date,
                    procurement_procedure__in=contracts,
                ).aggregate(Sum("contract_value_usd"))
                b["country"] = j.name
                b["country_code"] = j.country_code_alpha_2
                b["country_continent"] = j.continent
                if tender["contract_value_usd__sum"] is None:
                    tender_val = 0
                else:
                    tender_val = tender["contract_value_usd__sum"]
                if tender_count is None:
                    contract_val = 0
                else:
                    contract_val = tender_count
                if bool(temp) and j.name in temp.keys():
                    current_val = temp[j.name]
                    cum_value = current_val + tender_val
                    temp[j.name] = cum_value
                    b["amount_usd"] = cum_value
                else:
                    temp[j.name] = tender_val
                    b["amount_usd"] = tender_val
                if bool(tender_temp) and j.name in tender_temp.keys():
                    current_val = tender_temp[j.name]
                    cum_value = current_val + contract_val
                    tender_temp[j.name] = cum_value
                    b["tender_count"] = cum_value
                else:
                    tender_temp[j.name] = contract_val
                    b["tender_count"] = contract_val
                result["details"].append(b)
            data.append(result)
        return JsonResponse({"result": data})
