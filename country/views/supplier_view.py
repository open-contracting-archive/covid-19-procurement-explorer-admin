from django.db.models import Sum
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from country.models import Supplier
from country.serializers import SupplierSerializer


class SupplierView(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    filter_backends = [OrderingFilter]
    serializer_class = SupplierSerializer
    ordering_fields = [
        "tender_count",
        "buyer_count",
        "product_category_count",
        "supplier_name",
        "country_name",
        "amount_usd",
        "amount_local",
    ]
    ordering = ["-id"]
    extensions_auto_optimize = True

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        instance = Supplier.objects.filter(id=pk)[0]
        return Response(self.get_serializer(instance).data)

    def get_queryset(self):
        #    country, buyer name, value range, red flag range
        country = self.request.GET.get("country", None)
        supplier_name = self.request.GET.get("supplier_name", None)
        product_id = self.request.GET.get("product", None)
        filter_args = {}
        annotate_args = {}
        if country:
            filter_args["tenders__country__country_code_alpha_2"] = country
        if supplier_name:
            filter_args["supplier_name__icontains"] = supplier_name
        if product_id:
            filter_args["tenders__goods_services__goods_services_category"] = product_id
        contract_value_usd = self.request.GET.get("contract_value_usd", None)
        value_comparison = self.request.GET.get("value_comparison", None)
        if contract_value_usd and value_comparison:
            if value_comparison == "gt":
                annotate_args["sum"] = Sum("tenders__goods_services__contract_value_usd")
                filter_args["sum__gte"] = contract_value_usd
            elif value_comparison == "lt":
                annotate_args["sum"] = Sum("tenders__goods_services__contract_value_usd")
                filter_args["sum__lte"] = contract_value_usd
        return Supplier.objects.annotate(**annotate_args).filter(**filter_args).distinct()
