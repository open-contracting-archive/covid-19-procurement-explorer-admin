from django.db import models

from country.models import Country


class OverallSummary(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="overall_summary")
    statistic = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.statistic

    class Meta:
        app_label = "country"
