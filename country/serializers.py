from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from django.db.models import Avg, Count, Min, Sum, Count,Window
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
    amount_local = serializers.SerializerMethodField()
    amount_usd = serializers.SerializerMethodField()
    average_red_flag = serializers.SerializerMethodField()
    country_code =  serializers.SerializerMethodField()
    country_name =  serializers.SerializerMethodField()
    product_category_count =  serializers.SerializerMethodField()
    buyer_count =  serializers.SerializerMethodField()
    tender_count =  serializers.SerializerMethodField()
    supplier_id = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = (
            'amount_local',
            'amount_usd',
            'average_red_flag',
            'supplier_id',
            'supplier_name',
            'country_code',
            'country_name',
            'product_category_count',
            'buyer_count',
            'tender_count'
            )

    def get_amount_usd(self, obj):
        supplier_related_tenders = obj.tenders.all()
        sum_result = supplier_related_tenders.aggregate(sum_usd=Sum('goods_services__contract_value_usd'))
        return sum_result['sum_usd']

    def get_amount_local(self, obj):
        supplier_related_tenders = obj.tenders.all()
        sum_result = supplier_related_tenders.aggregate(sum_local=Sum('goods_services__contract_value_local'))
        return sum_result['sum_local']

    def get_average_red_flag(self, obj):
        return 0

    def get_country_code(self, obj):
        tender_obj = obj.tenders.first()
        if tender_obj:
            return tender_obj.country.country_code

    def get_country_name(self, obj):
        tender_obj = obj.tenders.first()
        if tender_obj:
            return tender_obj.country.name

    def get_product_category_count(self, obj):
        supplier_related_tenders = obj.tenders.all()
        if supplier_related_tenders:
            product_category_count =  supplier_related_tenders.distinct('goods_services__goods_services_category').count()
            return product_category_count

    def get_buyer_count(self, obj):
        supplier_related_tenders = obj.tenders.all()
        if supplier_related_tenders:
            supplier_count = supplier_related_tenders.distinct('supplier_id').count()
            return supplier_count

    def get_tender_count(self, obj):
        supplier_related_tenders = obj.tenders.all()
        if supplier_related_tenders:
            tender_count =  supplier_related_tenders.count()
            return tender_count

    def get_supplier_id(self,obj):
        return obj.id


class BuyerSerializer(serializers.ModelSerializer):
    amount_local = serializers.SerializerMethodField()
    amount_usd = serializers.SerializerMethodField()
    average_red_flag = serializers.SerializerMethodField()
    country_code =  serializers.SerializerMethodField()
    country_name =  serializers.SerializerMethodField()
    product_category_count =  serializers.SerializerMethodField()
    supplier_count =  serializers.SerializerMethodField()
    tender_count =  serializers.SerializerMethodField()
    buyer_id = serializers.SerializerMethodField()

    class Meta:
        model = Buyer
        fields = (
            'amount_local',
            'amount_usd',
            'average_red_flag',
            'buyer_id',
            'buyer_name',
            'country_code',
            'country_name',
            'product_category_count',
            'supplier_count',
            'tender_count'
            )

    def get_amount_usd(self, obj):
        buyer_related_tenders = obj.tenders.all()
        sum_result = buyer_related_tenders.aggregate(sum_usd=Sum('goods_services__contract_value_usd'))
        return sum_result['sum_usd']

    def get_amount_local(self, obj):
        buyer_related_tenders = obj.tenders.all()
        sum_result = buyer_related_tenders.aggregate(sum_local=Sum('goods_services__contract_value_local'))
        return sum_result['sum_local']

    def get_average_red_flag(self, obj):
        return 0

    def get_country_code(self, obj):
        tender_obj = obj.tenders.first()
        if tender_obj:
            return tender_obj.country.country_code

    def get_country_name(self, obj):
        tender_obj = obj.tenders.first()
        if tender_obj:
            return tender_obj.country.name

    def get_product_category_count(self, obj):
        buyer_related_tenders = obj.tenders.all()
        if  buyer_related_tenders:
            product_category_count =  buyer_related_tenders.distinct('goods_services__goods_services_category').count()
            return product_category_count

    def get_supplier_count(self, obj):
        buyer_related_tenders = obj.tenders.all()
        if  buyer_related_tenders:
            supplier_count = buyer_related_tenders.distinct('supplier_id').count()
            return supplier_count

    def get_tender_count(self, obj):
        buyer_related_tenders = obj.tenders.all()
        if  buyer_related_tenders:
            tender_count =  buyer_related_tenders.count()
            return tender_count

    def get_buyer_id(self,obj):
        return obj.id


class TenderSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_alpha_code = serializers.CharField(source='country.country_code_alpha_2', read_only=True)
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
            'country_alpha_code',
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

