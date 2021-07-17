from django.db import models
from django.utils.translation import gettext_lazy as _


class GoodsServicesCategory(models.Model):
    category_name = models.CharField(
        verbose_name=_("Category name"), max_length=100, null=False, unique=True, db_index=True
    )
    category_desc = models.TextField(verbose_name=_("Category description"), null=True, blank=True)

    def __str__(self):
        return self.category_name

    class Meta:
        app_label = "country"
