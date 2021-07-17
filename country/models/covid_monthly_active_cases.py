from django.db import models
from django.utils.translation import gettext_lazy as _

from country.models import Country


class CovidMonthlyActiveCases(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="covid_monthly_active_cases")
    covid_data_date = models.DateField()
    active_cases_count = models.BigIntegerField(verbose_name=_("Active cases count"), null=True, blank=True)
    death_count = models.BigIntegerField(verbose_name=_("Death count"), null=True, blank=True)

    class Meta:
        app_label = "country"
