from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class FilterParametersSuppliers(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        country_code = self.request.GET.get("country", None)
        buyer_id = self.request.GET.get("buyer", None)

        filter_args = {"supplier__isnull": False}

        if buyer_id:
            filter_args = add_filter_args("buyer", buyer_id, filter_args)

        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code

        try:
            suppliers = (
                Tender.objects.filter(**filter_args).values("supplier__id", "supplier__supplier_name").distinct()
            )

            result = []

            for supplier in suppliers:
                data = {"id": supplier["supplier__id"], "name": supplier["supplier__supplier_name"]}

                if country_code:
                    data["country_code"] = country_code

                result.append(data)

            return JsonResponse(result, safe=False)

        except Exception:
            return JsonResponse([{"error": "Country code does not exists"}], safe=False)
