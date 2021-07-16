from django.db.models import Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Supplier, Tender
from visualization.helpers.general import page_expire_period


class SupplierProfileView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]

        try:
            instance = Supplier.objects.get(id=pk)
            supplier_detail = (
                Tender.objects.filter(supplier_id=pk)
                .values("country__name", "country__country_code_alpha_2")
                .annotate(
                    total_usd=Sum("contract_value_usd"),
                    total_local=Sum("contract_value_local"),
                )
            )
            tender_count = Tender.objects.filter(supplier_id=pk).count()
            data = {
                "name": instance.supplier_name,
                "id": pk,
                "code": instance.supplier_id,
                "address": instance.supplier_address,
                "amount_usd": supplier_detail[0]["total_usd"],
                "amount_local": supplier_detail[0]["total_local"],
                "tender_count": tender_count,
                "country_code": supplier_detail[0]["country__country_code_alpha_2"],
                "country_name": supplier_detail[0]["country__name"],
            }
            return JsonResponse(data, safe=False)
        except Exception:
            error = {"error": "Enter valid ID"}
            return JsonResponse(error, safe=False)
