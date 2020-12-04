from rest_framework import serializers

from country.models import Tender

class TenderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tender
        fields = ('contract_value_local', 'contract_value_usd')
