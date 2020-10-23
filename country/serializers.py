from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Country, Language, Tender


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = (
            'id',
            'name',
            'code',
        )


class TenderSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = Tender
        fields = (
            'id',
            'country',
            'country_name',
            'project_title',
            'procurement_method',
            'supplier_name',
            'status',
            'value_usd',
        )
