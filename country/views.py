from django.contrib import messages
from django.core import management
from django.db.models import Sum
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from content.models import DataImport
from country.models import ImportBatch
from country.tasks import delete_dataset, store_in_temp_table
from vizualization.views import add_filter_args

from .models import Buyer, Country, Language, OverallSummary, Supplier, Tender
from .serializers import (
    BuyerSerializer,
    CountrySerializer,
    LanguageSerializer,
    OverallStatSummarySerializer,
    SupplierSerializer,
    TenderSerializer,
)


class TenderPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "limit"
    max_page_size = 1000


class CountryView(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    lookup_field = "slug"
    extensions_auto_optimize = True

    def get_queryset(self):
        return Country.objects.all()

    @action(detail=False, methods=["get"])
    def choices(self, request):
        countries = Country.objects.all().order_by("name")
        serializer = self.get_serializer(countries, many=True)
        country_id_and_name = [{"id": country["id"], "name": _(country["name"])} for country in serializer.data]

        return Response(country_id_and_name)


class LanguageView(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    extensions_auto_optimize = True


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
    filterset_fields = {
        "country__country_code_alpha_2": ["exact"],
    }
    extensions_auto_optimize = True

    def get_queryset(self):
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer", None)
        supplier = self.request.GET.get("supplier", None)
        product_id = self.request.GET.get("product", None)
        status = self.request.GET.get("status", None)
        procurement_procedure = self.request.GET.get("procurement_procedure", None)
        title = self.request.GET.get("title", None)
        date_from = self.request.GET.get("date_from", None)
        date_to = self.request.GET.get("date_to", None)
        contract_value_usd = self.request.GET.get("contract_value_usd", None)
        value_comparison = self.request.GET.get("value_comparison", None)
        equity_id = self.request.GET.get("equity_id", None)
        filter_args = {}
        exclude_args = {}
        annotate_args = {}
        if equity_id:
            filter_args["equity_category__id"] = equity_id
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)
        if product_id:
            filter_args["goods_services__goods_services_category"] = product_id
        if title:
            filter_args["contract_title__icontains"] = title
        if date_from and date_to:
            filter_args["contract_date__range"] = [date_from, date_to]
        if contract_value_usd and value_comparison:
            if value_comparison == "gt":
                annotate_args["sum"] = Sum("goods_services__contract_value_usd")
                filter_args["sum__gte"] = contract_value_usd
            elif value_comparison == "lt":
                annotate_args["sum"] = Sum("goods_services__contract_value_usd")
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


class BuyerView(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    filter_backends = [OrderingFilter]
    serializer_class = BuyerSerializer
    ordering_fields = [
        "tender_count",
        "supplier_count",
        "product_category_count",
        "buyer_name",
        "country_name",
        "amount_usd",
        "amount_local",
    ]
    ordering = ["-id"]
    extensions_auto_optimize = True

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        instance = Buyer.objects.filter(id=pk)[0]
        return Response(self.get_serializer(instance).data)

    def get_queryset(self):
        #    country, buyer name, value range, red flag range
        country = self.request.GET.get("country", None)
        buyer_name = self.request.GET.get("buyer_name", None)
        product_id = self.request.GET.get("product", None)
        contract_value_usd = self.request.GET.get("contract_value_usd", None)
        value_comparison = self.request.GET.get("value_comparison", None)
        filter_args = {}
        annotate_args = {}
        if country:
            filter_args["tenders__country__country_code_alpha_2"] = country
        if buyer_name:
            filter_args["buyer_name__contains"] = buyer_name
        if product_id:
            filter_args["tenders__goods_services__goods_services_category"] = product_id
        if contract_value_usd and value_comparison:
            if value_comparison == "gt":
                annotate_args["sum"] = Sum("tenders__goods_services__contract_value_usd")
                filter_args["sum__gte"] = contract_value_usd
            elif value_comparison == "lt":
                annotate_args["sum"] = Sum("tenders__goods_services__contract_value_usd")
                filter_args["sum__lte"] = contract_value_usd
        return Buyer.objects.prefetch_related("tenders").annotate(**annotate_args).filter(**filter_args).distinct()


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


class OverallStatSummaryView(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = OverallSummary.objects.all()
    serializer_class = OverallStatSummarySerializer
    extensions_auto_optimize = True


class DataImportView(APIView):
    def get(self, request):
        country = self.request.GET.get("country", None)
        # filename =  self.request.GET.get('filename',None)
        data_import_id = self.request.GET.get("data_import_id", None)
        validated = self.request.GET.get("validated", None)

        if validated:
            if data_import_id:
                try:
                    import_batch_instance = ImportBatch.objects.get(data_import_id=data_import_id)
                    batch_id = import_batch_instance.id
                    # management.call_command('import_tender_excel', country, file_path)
                    management.call_command("import_tender_from_id", country, batch_id)
                    messages.info(request, "Your import has started!")
                    return HttpResponseRedirect("/admin/content/dataimport")

                except Exception:
                    messages.error(request, "Your import has failed!")
                    return HttpResponseRedirect("/admin/content/dataimport")
            else:
                # messages.error(request, 'Your import failed because it only supports .xlsx and .xls file!')
                messages.error(request, "Your import failed!")
                return HttpResponseRedirect("/admin/content/dataimport")
        else:
            messages.error(
                request,
                "Your data import file is not validated, please upload file with all necessary headers and try "
                "importing again.",
            )

            return HttpResponseRedirect("/admin/content/dataimport")


class DataEditView(APIView):
    def get(self, request):
        data_import_id = self.request.GET.get("data_import_id", None)

        return HttpResponseRedirect("/admin/country/tempdataimporttable/?import_batch__id__exact=" + data_import_id)


class DataValidateView(APIView):
    def get(self, request):
        instance_id = self.request.GET.get("data_import_id", None)
        if instance_id is not None:
            try:
                store_in_temp_table.apply_async(args=(instance_id,), queue="covid19")
                messages.info(request, "Validation is in progress!! Please wait for a while")
                return HttpResponseRedirect("/admin/content/dataimport")

            except Exception:
                messages.error(request, "Your import has failed!")
                return HttpResponseRedirect("/admin/content/dataimport")
        else:
            # messages.error(request, 'Your import failed because it only supports .xlsx and .xls file!')
            messages.error(request, "Your import failed !!")
            return HttpResponseRedirect("/admin/content/dataimport")


class DeleteDataSetView(APIView):
    def get(self, request):
        data_import_id = self.request.GET.get("data_import_id", None)
        if data_import_id is not None:
            data_import = DataImport.objects.get(page_ptr_id=data_import_id)
            data_import.delete()
            delete_dataset.apply_async(args=(data_import_id,), queue="covid19")
            messages.info(request, "Your dataset has been successfully deleted from the system !!")
            return HttpResponseRedirect("/admin/content/dataimport")
        else:
            messages.error(request, "Invalid data import id !!")
            return HttpResponseRedirect("/admin/content/dataimport")
