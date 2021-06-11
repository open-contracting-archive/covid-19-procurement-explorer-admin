from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class FilterParametersBuyers(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        country_code = self.request.GET.get("country", None)
        supplier_id = self.request.GET.get("supplier", None)

        filter_args = {"buyer__isnull": False}

        if supplier_id:
            filter_args = add_filter_args("supplier", supplier_id, filter_args)

        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code

        try:
            buyers = Tender.objects.filter(**filter_args).values("buyer__id", "buyer__buyer_name").distinct()

            result = []
            for buyer in buyers:
                data = {"id": buyer["buyer__id"], "name": buyer["buyer__buyer_name"]}

                if country_code:
                    data["country_code"] = country_code

                result.append(data)

            return JsonResponse(result, safe=False)

        except Exception:
            return JsonResponse([{"error": "Country code does not exists"}], safe=False)
