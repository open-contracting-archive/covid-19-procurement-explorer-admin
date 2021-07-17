from django.db import models
from django.utils.translation import gettext_lazy as _

from country.models import Country


class ImportBatch(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="import_batch_country", null=True)
    import_type = models.CharField(verbose_name=_("Import Type"), max_length=150, null=False)
    description = models.CharField(verbose_name=_("Description"), max_length=500, null=False)
    data_import_id = models.IntegerField(null=True)

    def __str__(self):
        return f"Import batch id: {str(self.id)}"

    class Meta:
        app_label = "country"
