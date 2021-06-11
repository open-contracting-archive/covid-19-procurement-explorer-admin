from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from country.models import OverallSummary
from country.serializers import OverallStatSummarySerializer


class OverallStatSummaryView(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = OverallSummary.objects.all()
    serializer_class = OverallStatSummarySerializer
    extensions_auto_optimize = True
