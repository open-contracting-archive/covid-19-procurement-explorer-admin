from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import RedFlag, Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class ContractRedFlagsView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        supplier = self.request.GET.get("supplier", None)
        buyer = self.request.GET.get("buyer", None)
        product = self.request.GET.get("product", None)
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
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
