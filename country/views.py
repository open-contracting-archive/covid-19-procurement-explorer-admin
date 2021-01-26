from django.shortcuts import render
from django.utils import translation
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Min, Sum, Count,Window
from .models import Country, Language, Tender,Supplier,Buyer
from .serializers import CountrySerializer, LanguageSerializer, TenderSerializer ,SupplierSerializer,BuyerSerializer
from vizualization.views import add_filter_args
from django_filters import rest_framework as filters
from django.contrib.postgres.search import SearchVector

class TenderPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'limit'
    max_page_size = 1000

class CountryView(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Country.objects.all()
        return queryset

    @action(detail=False, methods=['get'])
    def choices(self, request):
        countries = Country.objects.all().order_by('name')
        serializer = self.get_serializer(countries, many=True)
        country_id_and_name = [{'id': country['id'], 'name': _(icountry['name'])} for country in serializer.data]

        return Response(country_id_and_name)


class LanguageView(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class TenderView(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ['-id']
    serializer_class = TenderSerializer
    ordering_fields = ('contract_title','procurement_procedure','supplier','status','contract_value_usd','buyer')
    filterset_fields = {
        'country__country_code_alpha_2': ['exact'],
    }

    def get_queryset(self):
        country =  self.request.GET.get('country',None)
        buyer = self.request.GET.get('buyer',None)
        supplier = self.request.GET.get('supplier',None)
        product_id = self.request.GET.get('product',None)
        status = self.request.GET.get('status',None)
        procurement_procedure = self.request.GET.get('procurement_procedure',None)
        title = self.request.GET.get('title',None)
        date_from = self.request.GET.get('date_from',None)
        date_to = self.request.GET.get('date_to',None)
        contract_value_usd = self.request.GET.get('contract_value_usd',None)
        value_comparison = self.request.GET.get('value_comparison',None)
        equity_id = self.request.GET.get('equity_id',None)
        filter_args = {}
        exclude_args={}
        annotate_args= {}
        if equity_id: filter_args['equity_category__id'] = equity_id
        if country: filter_args['country__country_code_alpha_2'] = country
        if buyer: filter_args = add_filter_args('buyer',buyer,filter_args)
        if supplier: filter_args = add_filter_args('supplier',supplier,filter_args)
        if product_id: filter_args['goods_services__goods_services_category'] = product_id
        if title: filter_args['contract_title__icontains'] = title
        if date_from and date_to : filter_args['contract_date__range'] = [date_from,date_to]
        if contract_value_usd and value_comparison : 
            if value_comparison == "gt":
                annotate_args['sum'] = Sum('goods_services__contract_value_usd')
                filter_args['sum__gte'] = contract_value_usd
            elif value_comparison == "lt":
                annotate_args['sum'] = Sum('goods_services__contract_value_usd')
                filter_args['sum__lte'] = contract_value_usd
        if status=="others":
            exclude_args['status__in'] = ['active','canceled','completed']
        elif status in ['active','canceled','completed']:
            filter_args['status'] = status
        if procurement_procedure=="others":
            exclude_args['procurement_procedure__in'] = ['open','limited','direct','selective']
        elif procurement_procedure in ['open','limited','direct','selective']:
            filter_args['procurement_procedure'] = procurement_procedure
        queryset = Tender.objects.annotate(**annotate_args).filter(**filter_args).exclude(**exclude_args)
        return queryset


class BuyerView(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    serializer_class = BuyerSerializer

    def get_queryset(self):
    #    country, buyer name, value range, red flag range
        country =  self.request.GET.get('country',None)
        buyer_name =  self.request.GET.get('buyer_name',None)
        product_id =  self.request.GET.get('product',None)
        contract_value_usd = self.request.GET.get('contract_value_usd',None)
        value_comparison = self.request.GET.get('value_comparison',None)
        filter_args = {}
        annotate_args= {}
        if country: filter_args['tenders__country__country_code_alpha_2'] = country
        if buyer_name: filter_args['buyer_name__icontains'] = buyer_name
        if product_id: filter_args['tenders__goods_services__goods_services_category'] = product_id
        if contract_value_usd and value_comparison : 
            if value_comparison == "gt":
                annotate_args['sum'] = Sum('tenders__goods_services__contract_value_usd')
                filter_args['sum__gte'] = contract_value_usd
            elif value_comparison == "lt":
                annotate_args['sum'] = Sum('tenders__goods_services__contract_value_usd')
                filter_args['sum__lte'] = contract_value_usd
        queryset = Buyer.objects.annotate(**annotate_args).filter(**filter_args).distinct()    
        return queryset

class SupplierView(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    serializer_class = SupplierSerializer

    def get_queryset(self):
    #    country, buyer name, value range, red flag range
        country =  self.request.GET.get('country',None)
        supplier_name =  self.request.GET.get('supplier_name',None)
        product_id =  self.request.GET.get('product_id',None)
        filter_args = {}
        annotate_args= {}
        if country: filter_args['tenders__country__country_code_alpha_2'] = country
        if supplier_name: filter_args['supplier_name__icontains'] = supplier_name
        if product_id: filter_args['tenders__goods_services__goods_services_category'] = product_id
        contract_value_usd = self.request.GET.get('contract_value_usd',None)
        value_comparison = self.request.GET.get('value_comparison',None)
        if contract_value_usd and value_comparison : 
            if value_comparison == "gt":
                annotate_args['sum'] = Sum('tenders__goods_services__contract_value_usd')
                filter_args['sum__gte'] = contract_value_usd
            elif value_comparison == "lt":
                annotate_args['sum'] = Sum('tenders__goods_services__contract_value_usd')
                filter_args['sum__lte'] = contract_value_usd
        queryset = Supplier.objects.annotate(**annotate_args).filter(**filter_args).distinct()
        return queryset