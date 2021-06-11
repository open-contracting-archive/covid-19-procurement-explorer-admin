from django.apps import AppConfig


class ContentConfig(AppConfig):
    name = "content"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        import content.signals  # noqa: F401
