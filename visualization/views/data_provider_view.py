from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.views import APIView

from country.models import DataProvider
from helpers.general import page_expire_period


class DataProviderView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        country_code = self.request.GET.get("country", None)

        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code

        try:
            data_provider = DataProvider.objects.filter(**filter_args)
            result = []

            if data_provider:
                for i in data_provider:
                    data = {
                        "name": i.name,
                        "country": str(i.country),
                        "website": i.website,
                        "logo": str(i.logo),
                        "remark": i.remark,
                    }
                    result.append(data)

            return JsonResponse(result, safe=False, status=status.HTTP_200_OK)

        except Exception:
            error = {"error": "Data Provider not found for this country"}

        return JsonResponse(error, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
