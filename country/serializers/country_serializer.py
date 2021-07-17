from django.db.models import Count, Max, Sum
from rest_framework import serializers
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin

from country.models import Country


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
            return obj.tenders.aggregate(amount_usd=Sum("contract_value_usd"))["amount_usd"]

    def get_amount_local(self, obj):
        try:
            if obj.amount_local:
                return obj.amount_local
            else:
                return None

        except Exception:
            return obj.tenders.aggregate(amount_local=Sum("contract_value_local"))["amount_local"]

    def get_tender_count(self, obj):
        try:
            if obj.tender_count:
                return obj.tender_count
            else:
                return None

        except Exception:
            return obj.tenders.aggregate(tender_count=Count("id"))["tender_count"]

    def get_last_contract_date(self, obj):
        try:
            if obj.last_contract_date:
                return obj.last_contract_date
            else:
                return None

        except Exception:
            return obj.tenders.aggregate(contract_last_date=Max("contract_date"))["contract_last_date"]
