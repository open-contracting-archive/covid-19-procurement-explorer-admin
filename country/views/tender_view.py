from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination

from country.models import Tender
from country.serializers import TenderSerializer
from visualization.views.lib.general import add_filter_args


class TenderView(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ["-id"]
    serializer_class = TenderSerializer
    ordering_fields = (
        "contract_title",
        "procurement_procedure",
        "supplier",
        "status",
        "contract_value_usd",
        "buyer",
        "contract_value_local",
        "country",
        "contract_date",
    )
    filter_set_fields = {
        "country__country_code_alpha_2": ["exact"],
    }
    extensions_auto_optimize = True

    def get_queryset(self):
        country_code = self.request.GET.get("country", None)
        buyer_id = self.request.GET.get("buyer", None)
        supplier_id = self.request.GET.get("supplier", None)
        product_id = self.request.GET.get("product", None)
        status = self.request.GET.get("status", None)
        procurement_procedure = self.request.GET.get("procurement_procedure", None)
        title = self.request.GET.get("title", None)
        date_from = self.request.GET.get("date_from", None)
        date_to = self.request.GET.get("date_to", None)
        contract_value_usd = self.request.GET.get("contract_value_usd", None)
        value_comparison = self.request.GET.get("value_comparison", None)
        red_flag_id = self.request.GET.get("red_flag", None)
        equity_id = self.request.GET.get("equity", None)
        filter_args = {}
        exclude_args = {}
        annotate_args = {}

        if equity_id:
            filter_args = add_filter_args("equity_category", equity_id, filter_args)
        if red_flag_id:
            filter_args["red_flag__id"] = red_flag_id
        if country_code:
            filter_args["country__country_code_alpha_2"] = country_code.upper()
        if buyer_id:
            filter_args = add_filter_args("buyer", buyer_id, filter_args)
        if supplier_id:
            filter_args = add_filter_args("supplier", supplier_id, filter_args)
        if product_id:
            filter_args["goods_services__goods_services_category"] = product_id
        if title:
            filter_args["contract_title__icontains"] = title
        if date_from and date_to:
            filter_args["contract_date__range"] = [date_from, date_to]
        if contract_value_usd and value_comparison:
            if value_comparison == "gt":
                annotate_args["sum"] = Sum("contract_value_usd")
                filter_args["sum__gte"] = contract_value_usd
            elif value_comparison == "lt":
                annotate_args["sum"] = Sum("contract_value_usd")
                filter_args["sum__lte"] = contract_value_usd
        if status == "others":
            exclude_args["status__in"] = ["active", "canceled", "completed"]
        elif status in ["active", "canceled", "completed"]:
            filter_args["status"] = status
        if procurement_procedure == "others":
            exclude_args["procurement_procedure__in"] = ["open", "limited", "direct", "selective"]
        elif procurement_procedure in ["open", "limited", "direct", "selective"]:
            filter_args["procurement_procedure"] = procurement_procedure
        return (
            Tender.objects.prefetch_related("buyer", "supplier", "country")
            .annotate(**annotate_args)
            .filter(**filter_args)
            .exclude(**exclude_args)
        )
