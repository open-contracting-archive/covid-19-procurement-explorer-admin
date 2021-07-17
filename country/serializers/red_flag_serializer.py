from rest_framework import serializers
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin

from country.models import RedFlag


class RedFlagSerializer(serializers.ModelSerializer, SerializerExtensionsMixin):
    class Meta:
        model = RedFlag
        fields = "__all__"
