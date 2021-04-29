from django.db.models import Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, Tender
from visualization.helpers.general import page_expire_period


class CountryMapView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        country = self.request.GET.get("country", None)
        try:
            country_instance = Country.objects.get(country_code_alpha_2=country)
        except Exception:
            return JsonResponse({"result": "Invalid Alpha Code"})
        if country is not None and country_instance is not None:
            tender_instance = Tender.objects.filter(country__country_code_alpha_2=country).aggregate(
                total_usd=Sum("goods_services__contract_value_usd"),
                total_local=Sum("goods_services__contract_value_local"),
            )
            count = Tender.objects.filter(country__country_code_alpha_2=country).count()
            final = {}
            final["country_code"] = country_instance.country_code_alpha_2
            final["country"] = country_instance.name
            final["country_continent"] = country_instance.continent
            final["amount_usd"] = tender_instance["total_usd"]
            final["amount_local"] = tender_instance["total_local"]
            final["tender_count"] = count
        else:
            final = {"result": "Invalid Alpha Code"}
        return JsonResponse(final)
