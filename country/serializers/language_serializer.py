from rest_framework import serializers
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin

from country.models import Language


class LanguageSerializer(serializers.ModelSerializer, SerializerExtensionsMixin):
    class Meta:
        model = Language
        fields = (
            "id",
            "name",
            "code",
        )
