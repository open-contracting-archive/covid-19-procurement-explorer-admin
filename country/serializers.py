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
    # red_flag_tender_count = serializers.SerializerMethodField()
    # red_flag_tender_percentage = serializers.SerializerMethodField()
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
            # "red_flag_tender_count",
            "supplier_id",
            "supplier_code",
            "supplier_name",
            "supplier_address",
            "country_code",
            "country_name",
            "product_category_count",
            "buyer_count",
            "tender_count",
            # "red_flag_tender_percentage",
        )

    def get_amount_usd(self, obj):
        try:
            if obj.amount_usd:
                return obj.amount_usd
            else:
                return None
        except Exception:
            return obj.tenders.all().aggregate(sum_usd=Sum("goods_services__contract_value_usd"))["sum_usd"]

    def get_amount_local(self, obj):
        try:
            if obj.amount_local:
                return obj.amount_local
            else:
                return None
        except Exception:
            return obj.tenders.all().aggregate(sum_local=Sum("goods_services__contract_value_local"))["sum_local"]

    # def get_red_flag_tender_count(self, obj):
    #     return obj.red_flag_count
    #
    # def get_red_flag_tender_percentage(self, obj):
    #     red_flags = obj.red_flag_count
    #     total = obj.tender_count
    #     try:
    #         return red_flags / total
    #     except Exception:
    #         return 0

    def get_country_code(self, obj):
        tender_obj = obj.tenders.first()
        if tender_obj:
            return tender_obj.country.country_code_alpha_2

    def get_country_name(self, obj):
        try:
            if obj.country_name:
                return obj.country_name
            else:
                return None
        except Exception:
            tender_obj = obj.tenders.first()
            if tender_obj:
                return tender_obj.country.name

    def get_buyer_count(self, obj):
        supplier_related_tenders = obj.tenders.all()
        if supplier_related_tenders:
            return supplier_related_tenders.exclude(buyer_id__isnull=True).distinct("buyer_id").count()

    def get_supplier_id(self, obj):
        return obj.id

    def get_tender_count(self, obj):
        try:
            if obj.tender_count:
                return obj.tender_count
            else:
                return None
        except Exception:
            supplier_related_tenders = obj.tenders.all()
            if supplier_related_tenders:
                return supplier_related_tenders.count()

    def get_product_category_count(self, obj):
        try:
            if obj.product_category_count:
                return obj.product_category_count
            else:
                return None
        except Exception:
            supplier_related_tenders = obj.tenders.all()
            if supplier_related_tenders:
                product_category_count = supplier_related_tenders.distinct(
                    "goods_services__goods_services_category"
                ).count()
                return product_category_count

    def get_supplier_code(self, obj):
        return obj.supplier_id


class BuyerSerializer(serializers.ModelSerializer, SerializerExtensionsMixin):
    amount_local = serializers.SerializerMethodField()
    amount_usd = serializers.SerializerMethodField()
    # red_flag_tender_count = serializers.SerializerMethodField()
    # red_flag_tender_percentage = serializers.SerializerMethodField()
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
            # "red_flag_tender_count",
            "buyer_id",
            "buyer_code",
            "buyer_name",
            "buyer_address",
            "country_code",
            "country_name",
            "product_category_count",
            "supplier_count",
            "tender_count",
            # "red_flag_tender_percentage",
        )

    def get_amount_usd(self, obj):
        try:
            if obj.amount_usd:
                return obj.amount_usd
            else:
                return None
        except Exception:
            return (
                obj.tenders.select_related("goods_services")
                .all()
                .aggregate(sum_usd=Sum("goods_services__contract_value_usd"))["sum_usd"]
            )

    def get_amount_local(self, obj):
        try:
            if obj.amount_local:
                return obj.amount_local
            else:
                return None
        except Exception:
            return (
                obj.tenders.select_related("goods_services")
                .all()
                .aggregate(sum_local=Sum("goods_services__contract_value_local"))["sum_local"]
            )

    # def get_red_flag_tender_count(self, obj):
    #     return obj.red_flag_count
    #
    # def get_red_flag_tender_percentage(self, obj):
    #     red_flags = obj.red_flag_count
    #     total = obj.tender_count
    #     try:
    #         return red_flags / total
    #     except Exception:
    #         return 0

    def get_country_code(self, obj):
        tender_obj = obj.tenders.first()
        if tender_obj:
            return tender_obj.country.country_code_alpha_2

    def get_country_name(self, obj):
        try:
            if obj.country_name:
                return obj.country_name
            else:
                return None
        except Exception:
            tender_obj = obj.tenders.first()
            if tender_obj:
                return tender_obj.country.name

    def get_product_category_count(self, obj):
        try:
            if obj.product_category_count:
                return obj.product_category_count
            else:
                return None
        except Exception:
            buyer_related_tenders = obj.tenders.all()
            if buyer_related_tenders:
                product_category_count = buyer_related_tenders.distinct(
                    "goods_services__goods_services_category"
                ).count()
                return product_category_count

    def get_supplier_count(self, obj):
        buyer_related_tenders = obj.tenders.all()
        if buyer_related_tenders:
            return buyer_related_tenders.exclude(supplier_id__isnull=True).distinct("supplier_id").count()

    def get_tender_count(self, obj):
        try:
            if obj.tender_count:
                return obj.tender_count
            else:
                return None
        except Exception:
            buyer_related_tenders = obj.tenders.all()
            if buyer_related_tenders:
                return buyer_related_tenders.count()

    def get_buyer_id(self, obj):
        return obj.id

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
    contract_value_usd = serializers.SerializerMethodField()
    contract_value_local = serializers.SerializerMethodField()
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
    tender_local = serializers.SerializerMethodField()
    tender_usd = serializers.SerializerMethodField()
    award_local = serializers.SerializerMethodField()
    award_usd = serializers.SerializerMethodField()
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
            "tender_local",
            "tender_usd",
            "award_local",
            "award_usd",
            "equity_category",
            # 'red_flag_count',
            "red_flag",
            "goods_services",
        )
        read_only_fields = (
            "contract_value_usd",
            "contract_currency_local",
        )

    def get_contract_value_usd(self, obj):
        return obj.goods_services.aggregate(total=Sum("contract_value_usd"))["total"]

    def get_contract_value_local(self, obj):
        return obj.goods_services.aggregate(total=Sum("contract_value_local"))["total"]

    def get_product_category(self, obj):
        tender = (
            Tender.objects.filter(id=obj.id)
            .values("goods_services__goods_services_category__category_name")
            .distinct()
        )
        return tender[0]["goods_services__goods_services_category__category_name"]

    def get_bidders_no(self, obj):
        try:
            return obj.no_of_bidders
        except Exception:
            return 0

    def get_tender_local(self, obj):
        try:
            return obj.goods_services.aggregate(tender_value_local=Sum("tender_value_local"))["tender_value_local"]
        except Exception:
            return 0

    def get_tender_usd(self, obj):
        try:
            return obj.goods_services.aggregate(tender_value_usd=Sum("tender_value_usd"))["tender_value_usd"]
        except Exception:
            return 0

    def get_award_local(self, obj):
        try:
            return obj.goods_services.aggregate(award_value_local=Sum("award_value_local"))["award_value_local"]
        except Exception:
            return 0

    def get_award_usd(self, obj):
        try:
            return obj.goods_services.aggregate(award_value_usd=Sum("award_value_usd"))["award_value_usd"]
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
        a = obj.goods_services.all().values(
            "goods_services_category__category_name",
            "contract_desc",
            "contract_value_usd",
            "quantity_units",
            "ppu_including_vat",
            "contract_value_local",
            "classification_code",
        )
        return list(a)


class OverallStatSummarySerializer(serializers.ModelSerializer, SerializerExtensionsMixin):
    country = CountrySerializer(many=False, read_only=True)

    class Meta:
        model = OverallSummary
        fields = "__all__"
