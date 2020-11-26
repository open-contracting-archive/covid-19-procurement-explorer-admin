from django.shortcuts import render
from django.utils import translation
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Country, Language, Tender
from .serializers import CountrySerializer, LanguageSerializer, TenderSerializer


class CountryView(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

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
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class TenderPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class TenderView(viewsets.ModelViewSet):
    pagination_class = TenderPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ['-id']
    queryset = Tender.objects.all()
    serializer_class = TenderSerializer
    ordering_fields = ('contract_title','procurement_procedure','supplier','status','contract_value_usd')
    filterset_fields = {
        'country': ['exact'],
        'country__name': ['exact'],
        'status': ['exact'],
        'procurement_procedure': ['exact'],
        'supplier__supplier_id': ['exact'],
    }
