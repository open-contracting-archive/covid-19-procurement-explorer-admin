from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Country, Language, Tender, Supplier


class CountrySerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Country
        fields = '__all__'
        lookup_field = 'slug'

        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

        read_only_fields = (
            'covid_cases_total',
            'covid_deaths_total',
            'covid_data_last_updated',
            'slug',
            )


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = (
            'id',
            'name',
            'code',
        )


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = (
            'id',
            'supplier_id',
            'supplier_name',
            )


class TenderSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    contract_currency_local = serializers.CharField(source='country.currency', read_only=True)
    supplier = SupplierSerializer(read_only=True)

    class Meta:
        model = Tender
        fields = (
            'id',
            'country',
            'country_name',
            'contract_date',
            'contract_id',
            'contract_title',
            'contract_desc',
            'contract_value_usd',
            'contract_value_local',
            'contract_currency_local',
            'procurement_procedure',
            'status',
            'supplier',
            'link_to_contract',
            'link_to_tender',
            'data_source'
        )
        read_only_fields = (
            'contract_value_usd',
            'contract_currency_local',
        )
