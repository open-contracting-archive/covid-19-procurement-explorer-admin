from django.db.models import Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, Tender
from visualization.helpers.general import page_expire_period


class WorldMapView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        product = self.request.GET.get("product", None)
        filter_args = {}
        if product:
            filter_args["goods_services__goods_services_category__id"] = product
        country_instance = Country.objects.all().exclude(country_code_alpha_2="gl")
        result = []
        for country in country_instance:
            data = {}
            tender_instance = Tender.objects.filter(country=country, **filter_args).aggregate(
                total_usd=Sum("contract_value_usd")
            )
            tender_count = Tender.objects.filter(country=country, **filter_args).count()
            data["country_code"] = country.country_code_alpha_2
            data["country"] = country.name
            data["country_continent"] = country.continent
            data["amount_usd"] = tender_instance["total_usd"]
            data["tender_count"] = tender_count
            result.append(data)
        return JsonResponse({"result": result})
