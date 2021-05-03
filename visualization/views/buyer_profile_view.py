from django.db.models import Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.views import APIView

from country.models import Buyer
from visualization.helpers.general import page_expire_period


class BuyerProfileView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        try:
            instance = Buyer.objects.get(id=pk)
            tenders = instance.tenders
            buyer_detail = (
                tenders.values("country__name", "country__country_code_alpha_2")
                .annotate(
                    total_usd=Sum("contract_value_usd"),
                    total_local=Sum("contract_value_local"),
                )
                .first()
            )
            data = {
                "name": instance.buyer_name,
                "id": pk,
                "code": instance.buyer_id,
                "address": instance.buyer_address,
                "amount_usd": buyer_detail.get("total_usd", 0),
                "amount_local": buyer_detail.get("total_local", 0),
                "tender_count": tenders.distinct().count(),
                "country_code": buyer_detail.get("country__country_code_alpha_2", ""),
                "country_name": buyer_detail.get("country__name", ""),
            }
            return JsonResponse(data, safe=False, status=status.HTTP_200_OK)
        except Exception as E:
            error = {"error": str(E)}
            return JsonResponse(error, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
