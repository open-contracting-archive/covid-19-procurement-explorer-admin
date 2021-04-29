from django.db.models import Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Buyer, Tender
from visualization.helpers.general import page_expire_period


class BuyerProfileView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        data = {}
        try:
            instance = Buyer.objects.get(id=pk)
            buyer_detail = (
                Tender.objects.filter(buyer_id=pk)
                .values("country__name", "country__country_code_alpha_2")
                .annotate(
                    total_usd=Sum("goods_services__contract_value_usd"),
                    total_local=Sum("goods_services__contract_value_local"),
                )
            )
            tender_count = Tender.objects.filter(buyer_id=pk).count()
            data["name"] = instance.buyer_name
            data["id"] = pk
            data["code"] = instance.buyer_id
            data["address"] = instance.buyer_address
            data["amount_usd"] = buyer_detail[0]["total_usd"]
            data["amount_local"] = buyer_detail[0]["total_local"]
            data["tender_count"] = tender_count
            data["country_code"] = buyer_detail[0]["country__country_code_alpha_2"]
            data["country_name"] = buyer_detail[0]["country__name"]
            return JsonResponse(data, safe=False)
        except Exception:
            data["error"] = "Enter valid ID"
            return JsonResponse(data, safe=False)
