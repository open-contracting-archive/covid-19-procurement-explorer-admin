from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import RedFlag, Tender
from helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class ContractRedFlagsView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        country_code = self.request.GET.get("country", None)
        supplier_id = self.request.GET.get("supplier", None)
        buyer_id = self.request.GET.get("buyer", None)
        product = self.request.GET.get("product", None)
        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code
        if supplier_id:
            filter_args = add_filter_args("supplier", supplier_id, filter_args)
        if buyer_id:
            filter_args = add_filter_args("buyer", buyer_id, filter_args)
        if product:
            filter_args["goods_services__goods_services_category__id"] = product
        red_flags = RedFlag.objects.filter(implemented=True)
        value = []
        result = {"result": value}
        for red_flag in red_flags:
            count = Tender.objects.filter(**filter_args, red_flag__pk=red_flag.id).distinct().count()
            data = {}
            data["red_flag_id"] = red_flag.id
            data["red_flag"] = red_flag.title
            data["tender_count"] = count
            value.append(data)
        return JsonResponse(result, safe=False)
