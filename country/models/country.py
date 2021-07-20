from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _


class CountryManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Country(models.Model):
    CONTINENT_CHOICES = [
        ("africa", "Africa"),
        ("asia", "Asia"),
        ("europe", "Europe"),
        ("middle_east", "Middle East"),
        ("north_america", "North America"),
        ("south_america", "South America"),
        ("oceanic", "Oceanic"),
    ]

    alphaSpaces = RegexValidator(r"^[a-zA-Z ]+$", "Only letters and spaces are allowed in the Country Name")

    slug = models.SlugField(null=True, unique=True)
    name = models.CharField(verbose_name=_("Name"), null=False, unique=True, max_length=50, validators=[alphaSpaces])
    continent = models.CharField(
        verbose_name=_("Continent"), max_length=25, choices=CONTINENT_CHOICES, null=True, blank=False
    )
    population = models.BigIntegerField(
        verbose_name=_("Population"), null=True, blank=True, validators=[MinValueValidator(0)]
    )
    gdp = models.FloatField(
        verbose_name=_("GDP per capita, $"), null=True, blank=True, validators=[MinValueValidator(0)]
    )
    country_code = models.CharField(verbose_name=_("Country code"), max_length=10, null=False)
    country_code_alpha_2 = models.CharField(
        verbose_name=_("Country code alpha-2"), max_length=2, null=False, db_index=True
    )
    currency = models.CharField(verbose_name=_("Currency"), max_length=50, null=False)
    healthcare_budget = models.FloatField(
        verbose_name=_("Healthcare spending, $ per capita"), null=True, blank=True, validators=[MinValueValidator(0)]
    )
    healthcare_gdp_pc = models.FloatField(
        verbose_name=_("% of GDP to healthcare"),
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    covid_cases_total = models.BigIntegerField(
        verbose_name=_("Total COVID-19 cases"), null=True, blank=True, validators=[MinValueValidator(0)]
    )
    covid_deaths_total = models.BigIntegerField(
        verbose_name=_("Total deaths by Covid-19"), null=True, blank=True, validators=[MinValueValidator(0)]
    )
    covid_active_cases = models.BigIntegerField(
        verbose_name=_("Active cases of Covid-19"), null=True, blank=True, validators=[MinValueValidator(0)]
    )
    covid_data_last_updated = models.DateTimeField(null=True, blank=True)

    objects = CountryManager()

    class Meta:
        verbose_name_plural = _("Countries")
        app_label = "country"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Country, self).save(*args, **kwargs)
