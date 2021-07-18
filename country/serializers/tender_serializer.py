from rest_framework import serializers
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin

from country.models import Tender
from country.serializers.red_flag_serializer import RedFlagSerializer


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
