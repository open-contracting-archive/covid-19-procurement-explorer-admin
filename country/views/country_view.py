from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from country.models import Country
from country.serializers import CountrySerializer


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
