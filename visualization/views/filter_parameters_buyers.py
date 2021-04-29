from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class FilterParametersBuyers(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        result = []
        country = self.request.GET.get("country", None)
        supplier = self.request.GET.get("supplier", None)
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)
        try:
            if country:
                filter_args["country__country_code_alpha_2"] = country
                instance = Country.objects.get(country_code_alpha_2=country)
                country_code = instance.country_code_alpha_2
            filter_args["buyer__isnull"] = False
            buyers = Tender.objects.filter(**filter_args).values("buyer__id", "buyer__buyer_name").distinct()
            for buyer in buyers:
                data = {}
                data["id"] = buyer["buyer__id"]
                data["name"] = buyer["buyer__buyer_name"]
                if country:
                    data["country_code"] = country_code
                else:
                    data["country_code"] = "USD"
                result.append(data)
            return JsonResponse(result, safe=False)
        except Exception:
            return JsonResponse([{"error": "Country code doest not exists"}], safe=False)
