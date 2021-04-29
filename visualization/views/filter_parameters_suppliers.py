from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class FilterParametersSuppliers(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        result = []
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer", None)
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        try:
            if country:
                filter_args["country__country_code_alpha_2"] = country
                instance = Country.objects.get(country_code_alpha_2=country)
                country_code = instance.country_code_alpha_2
            filter_args["supplier__isnull"] = False
            suppliers = (
                Tender.objects.filter(**filter_args).values("supplier__id", "supplier__supplier_name").distinct()
            )
            for supplier in suppliers:
                data = {}
                data["id"] = supplier["supplier__id"]
                data["name"] = supplier["supplier__supplier_name"]
                if country:
                    data["country_code"] = country_code
                else:
                    data["country_code"] = "USD"
                result.append(data)
            return JsonResponse(result, safe=False)
        except Exception:
            return JsonResponse([{"error": "Country code doest not exists"}], safe=False)
