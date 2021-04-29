from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from country.models import Language
from country.serializers import LanguageSerializer


class LanguageView(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    extensions_auto_optimize = True
