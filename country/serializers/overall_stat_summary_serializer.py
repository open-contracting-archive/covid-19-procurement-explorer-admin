from rest_framework import serializers
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin

from country.models import OverallSummary
from country.serializers.country_serializer import CountrySerializer


class OverallStatSummarySerializer(serializers.ModelSerializer, SerializerExtensionsMixin):
    country = CountrySerializer(many=False, read_only=True)

    class Meta:
        model = OverallSummary
        fields = "__all__"
