from django.db.models import Count, Max, Sum
from rest_framework import serializers
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin

from .models import Buyer, Country, Language, OverallSummary, RedFlag, Supplier, Tender


class ChoiceField(serializers.ChoiceField):
    def to_representation(self, obj):
        if obj == "" and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == "" and self.allow_blank:
            return ""

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail("invalid_choice", input=data)


class CountrySerializer(serializers.HyperlinkedModelSerializer, SerializerExtensionsMixin):
    id = serializers.IntegerField(read_only=True)
    continent = ChoiceField(choices=Country.CONTINENT_CHOICES)
    amount_usd = serializers.SerializerMethodField()
    amount_local = serializers.SerializerMethodField()
    tender_count = serializers.SerializerMethodField()
    last_contract_date = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = "__all__"
        extra_fields = ["continent", "id", "amount_usd", "amount_local", "tender_count"]
        lookup_field = "slug"

        extra_kwargs = {"url": {"lookup_field": "slug"}}

        read_only_fields = (
            "covid_cases_total",
            "covid_deaths_total",
            "covid_data_last_updated",
            "slug",
        )

    def get_amount_usd(self, obj):
        try:
            if obj.amount_usd:
                return obj.amount_usd
            else:
                None

        except Exception:
            return obj.tenders.all().aggregate(amount_usd=Sum("goods_services__contract_value_usd"))["amount_usd"]

    def get_amount_local(self, obj):
        try:
            if obj.amount_local:
                return obj.amount_local
            else:
                return None

        except Exception:
            return obj.tenders.all().aggregate(amount_local=Sum("goods_services__contract_value_local"))[
                "amount_local"
            ]

    def get_tender_count(self, obj):
        try:
            if obj.tender_count:
                return obj.tender_count
            else:
                return None

        except Exception:
            return obj.tenders.all().aggregate(tender_count=Count("id"))["tender_count"]

    def get_last_contract_date(self, obj):
        try:
            if obj.last_contract_date:
                return obj.last_contract_date
            else:
                return None

        except Exception:
            return obj.tenders.all().aggregate(contract_last_date=Max("contract_date"))["contract_last_date"]


class LanguageSerializer(serializers.ModelSerializer, SerializerExtensionsMixin):
    class Meta:
        model = Language
        fields = (
            "id",
            "name",
            "code",
        )


class SupplierSerializer(serializers.ModelSerializer, SerializerExtensionsMixin):
    amount_local = serializers.SerializerMethodField()
    amount_usd = serializers.SerializerMethodField()
    red_flag_tender_count = serializers.SerializerMethodField()
    red_flag_tender_percentage = serializers.SerializerMethodField()
    country_code = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    product_category_count = serializers.SerializerMethodField()
    buyer_count = serializers.SerializerMethodField()
    tender_count = serializers.SerializerMethodField()
    supplier_id = serializers.SerializerMethodField()
    supplier_code = serializers.SerializerMethodField(source="supplier.supplier_id", read_only=True)

    class Meta:
        model = Supplier
        fields = (
            "amount_local",
            "amount_usd",
            "red_flag_tender_count",
            "supplier_id",
            "supplier_code",
            "supplier_name",
            "supplier_address",
            "country_code",
            "country_name",
            "product_category_count",
            "buyer_count",
            "tender_count",
            "red_flag_tender_percentage",
        )

    def get_amount_usd(self, obj):
        try:
            amount_usd = obj.summary["amount_usd"]
        except TypeError:
            amount_usd = 0
        return amount_usd

    def get_amount_local(self, obj):
        try:
            amount_local = obj.summary["amount_local"]
        except TypeError:
            amount_local = 0
        return amount_local

    def get_red_flag_tender_count(self, obj):
        try:
            red_flag_tender_count = obj.summary["red_flag_tender_count"]
        except TypeError:
            red_flag_tender_count = 0
        return red_flag_tender_count

    def get_red_flag_tender_percentage(self, obj):
        try:
            red_flag_tender_percentage = round(obj.summary["red_flag_tender_percentage"], 2)
        except TypeError:
            red_flag_tender_percentage = 0
        return red_flag_tender_percentage

    def get_country_code(self, obj):
        try:
            country_code = obj.summary["country_code"]
        except TypeError:
            country_code = ""
        return country_code

    def get_country_name(self, obj):
        try:
            country_name = obj.summary["country_name"]
        except TypeError:
            country_name = ""
        return country_name

    def get_buyer_count(self, obj):
        try:
            buyer_count = obj.summary["buyer_count"]
        except TypeError:
            buyer_count = 0
        return buyer_count

    def get_supplier_id(self, obj):
        return obj.id

    def get_tender_count(self, obj):
        try:
            tender_count = obj.summary["tender_count"]
        except TypeError:
            tender_count = 0
        return tender_count

    def get_product_category_count(self, obj):
        try:
            product_count = obj.summary["product_count"]
        except TypeError:
            product_count = 0
        return product_count

    def get_supplier_code(self, obj):
        return obj.supplier_id


class BuyerSerializer(serializers.ModelSerializer, SerializerExtensionsMixin):
    amount_local = serializers.SerializerMethodField()
    amount_usd = serializers.SerializerMethodField()
    red_flag_tender_count = serializers.SerializerMethodField()
    red_flag_tender_percentage = serializers.SerializerMethodField()
    country_code = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    product_category_count = serializers.SerializerMethodField()
    supplier_count = serializers.SerializerMethodField()
    tender_count = serializers.SerializerMethodField()
    buyer_id = serializers.SerializerMethodField()
    buyer_code = serializers.SerializerMethodField(source="buyer.buyer_id", read_only=True)

    class Meta:
        model = Buyer
        fields = (
            "amount_local",
            "amount_usd",
            "red_flag_tender_count",
            "buyer_id",
            "buyer_code",
            "buyer_name",
            "buyer_address",
            "country_code",
            "country_name",
            "product_category_count",
            "supplier_count",
            "tender_count",
            "red_flag_tender_percentage",
        )

    def get_amount_usd(self, obj):
        try:
            amount_usd = obj.summary["amount_usd"]
        except TypeError:
            amount_usd = 0
        return amount_usd

    def get_amount_local(self, obj):
        try:
            amount_local = obj.summary["amount_local"]
        except TypeError:
            amount_local = 0
        return amount_local

    def get_red_flag_tender_count(self, obj):
        try:
            red_flag_tender_count = obj.summary["red_flag_tender_count"]
        except TypeError:
            red_flag_tender_count = 0
        return red_flag_tender_count

    def get_red_flag_tender_percentage(self, obj):
        try:
            red_flag_tender_percentage = round(obj.summary["red_flag_tender_percentage"], 2)
        except TypeError:
            red_flag_tender_percentage = 0
        return red_flag_tender_percentage

    def get_country_code(self, obj):
        try:
            country_code = obj.summary["country_code"]
        except TypeError:
            country_code = ""
        return country_code

    def get_country_name(self, obj):
        try:
            country_name = obj.summary["country_name"]
        except TypeError:
            country_name = ""
        return country_name

    def get_supplier_count(self, obj):
        try:
            supplier_count = obj.summary["supplier_count"]
        except TypeError:
            supplier_count = 0
        return supplier_count

    def get_buyer_id(self, obj):
        return obj.id

    def get_tender_count(self, obj):
        try:
            tender_count = obj.summary["tender_count"]
        except TypeError:
            tender_count = 0
        return tender_count

    def get_product_category_count(self, obj):
        try:
            product_count = obj.summary["product_count"]
        except TypeError:
            product_count = 0
        return product_count

    def get_buyer_code(self, obj):
        return obj.buyer_id


class RedFlagSerializer(serializers.ModelSerializer, SerializerExtensionsMixin):
    class Meta:
        model = RedFlag
        fields = "__all__"


class TenderSerializer(serializers.ModelSerializer, SerializerExtensionsMixin):
    country_name = serializers.CharField(source="country.name", read_only=True)
    country_alpha_code = serializers.CharField(source="country.country_code_alpha_2", read_only=True)
    contract_currency_local = serializers.CharField(source="country.currency", read_only=True)
    supplier_name = serializers.SerializerMethodField()
    buyer_name = serializers.SerializerMethodField()
    supplier_id = serializers.SerializerMethodField()
    buyer_id = serializers.SerializerMethodField()
    supplier_address = serializers.SerializerMethodField()
    buyer_address = serializers.SerializerMethodField()
    supplier_code = serializers.SerializerMethodField()
    buyer_code = serializers.SerializerMethodField()
    product_category = serializers.SerializerMethodField()
    bidders_no = serializers.SerializerMethodField()
    equity_category = serializers.SerializerMethodField()
    # red_flag_count = serializers.SerializerMethodField()
    red_flag = RedFlagSerializer(many=True, read_only=True)
    goods_services = serializers.SerializerMethodField()

    class Meta:
        model = Tender
        fields = (
            "id",
            "country",
            "country_name",
            "country_alpha_code",
            "contract_date",
            "contract_id",
            "contract_title",
            "contract_desc",
            "contract_value_usd",
            "contract_value_local",
            "contract_currency_local",
            "procurement_procedure",
            "status",
            "supplier_name",
            "buyer_name",
            "supplier_id",
            "buyer_id",
            "supplier_address",
            "buyer_address",
            "supplier_code",
            "buyer_code",
            "link_to_contract",
            "link_to_tender",
            "data_source",
            "product_category",
            "bidders_no",
            "tender_value_local",
            "tender_value_usd",
            "award_value_local",
            "award_value_usd",
            "equity_category",
            # 'red_flag_count',
            "red_flag",
            "goods_services",
        )
        read_only_fields = (
            "contract_value_usd",
            "contract_currency_local",
        )

    def get_product_category(self, obj):
        try:
            categories = obj.goods_services.values("goods_services_category__category_name").distinct()
            return categories[0]["goods_services_category__category_name"]
        except Exception:
            return ""

    def get_bidders_no(self, obj):
        try:
            return obj.no_of_bidders
        except Exception:
            return 0

    def get_equity_category(self, obj):
        equity_categories = obj.equity_category.all()
        result = []
        for equity in equity_categories:
            result.append(equity.category_name)
        return result

    def get_supplier_name(self, obj):
        if obj.supplier:
            return obj.supplier.supplier_name

    def get_buyer_name(self, obj):
        if obj.buyer:
            return obj.buyer.buyer_name

    def get_supplier_id(self, obj):
        if obj.supplier:
            return obj.supplier.id

    def get_buyer_id(self, obj):
        if obj.buyer:
            return obj.buyer.id

    def get_supplier_address(self, obj):
        if obj.supplier:
            return obj.supplier.supplier_address

    def get_buyer_address(self, obj):
        if obj.buyer:
            return obj.buyer.buyer_address

    def get_supplier_code(self, obj):
        if obj.supplier:
            return obj.supplier.supplier_id

    def get_buyer_code(self, obj):
        if obj.buyer:
            return obj.buyer.buyer_id

    def get_goods_services(self, obj):
        a = obj.goods_services.values(
            "goods_services_category__category_name",
            "contract_desc",
            "contract_value_usd",
            "quantity_units",
            "ppu_including_vat",
            "contract_value_local",
            "classification_code",
        )
        if obj.goods_services:
            return list(a)


class OverallStatSummarySerializer(serializers.ModelSerializer, SerializerExtensionsMixin):
    country = CountrySerializer(many=False, read_only=True)

    class Meta:
        model = OverallSummary
        fields = "__all__"
