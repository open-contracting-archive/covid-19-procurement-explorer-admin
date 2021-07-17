from django.db import models
from django.template.defaultfilters import slugify


class Topic(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(default="", editable=False, max_length=100)

    def save(self, *args, **kwargs):
        value = self.title
        self.slug = slugify(value)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        app_label = "country"
