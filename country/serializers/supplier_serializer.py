from rest_framework import serializers
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin

from country.models import Supplier


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
