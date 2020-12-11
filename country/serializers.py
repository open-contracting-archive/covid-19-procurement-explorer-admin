from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Country, Language, Tender, Supplier, Buyer


class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)


class CountrySerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    continent = ChoiceField(choices=Country.CONTINENT_CHOICES)

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
            'supplier_address',
            )


class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = (
            'id',
            'buyer_id',
            'buyer_name',
            'buyer_address',
            )


from django.db.models import Avg, Count, Min, Sum, Count,Window

class TenderSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    contract_currency_local = serializers.CharField(source='country.currency', read_only=True)
    contract_value_usd = serializers.SerializerMethodField()
    contract_value_local = serializers.SerializerMethodField()
    supplier = SupplierSerializer(read_only=True)
    buyer = BuyerSerializer(read_only=True)

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
            'buyer',
            'link_to_contract',
            'link_to_tender',
            'data_source'
        )
        read_only_fields = (
            'contract_value_usd',
            'contract_currency_local',
        )

    def get_contract_value_usd(self, obj):
        return obj.goods_services.aggregate(total=Sum('contract_value_usd'))['total']

    def get_contract_value_local(self, obj):
        return obj.goods_services.aggregate(total=Sum('contract_value_local'))['total']

