from django.db import models
from django.utils.translation import gettext_lazy as _


class EquityCategoryManager(models.Manager):
    def get_by_natural_key(self, category_name):
        return self.get(category_name=category_name)


class EquityCategory(models.Model):
    category_name = models.CharField(verbose_name=_("Category name"), max_length=50, null=True, unique=True)

    objects = EquityCategoryManager()

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Equity Categories"
        app_label = "country"
