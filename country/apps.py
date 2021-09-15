from django.apps import AppConfig


class CountryConfig(AppConfig):
    name = "country"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        import country.signals  # noqa: F401
