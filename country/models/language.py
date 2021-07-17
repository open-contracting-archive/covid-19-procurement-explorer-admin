from django.db import models


class Language(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "country"
