from django.db import models
from django.utils.translation import ugettext_lazy as _


class Country(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=50)
    population = models.IntegerField(verbose_name=_('Population'),null=True)
    gdp = models.FloatField(verbose_name=_('GDP'), null=True)
    currency = models.CharField(verbose_name=_('Currency'), max_length=5, null=True)
    healthcare_budget = models.FloatField(verbose_name=_('Healthcare budget'),null=True)
    healthcare_gdp_pc = models.FloatField(verbose_name=_('% of GDP to healthcare'), null=True)
    covid_cases_total = models.IntegerField(verbose_name=_('Total COVID-19 cases'), null=True)
    covid_deaths_total = models.IntegerField(verbose_name=_('Total deaths by Covid-19'), null=True)
    equity_unemployment_rate = models.FloatField(verbose_name=_('Unemployment rate'), null=True)
    equity_income_avg = models.FloatField(verbose_name=_('Average income'), null=True)
    equity_gender_dist_male = models.FloatField(verbose_name=_('Gender distribution male'), null=True)
    equity_gender_dist_female = models.FloatField(verbose_name=_('Gender distribution female'), null=True)
    equity_age_dist_0_14 = models.FloatField(verbose_name=_('Age distribution 0-14 years'), null=True)
    equity_age_dist_15_24 = models.FloatField(verbose_name=_('Age distribution 15-24 years'), null=True)
    equity_age_dist_25_54 = models.FloatField(verbose_name=_('Age distribution 25-54 years'), null=True)
    equity_age_dist_55_64 = models.FloatField(verbose_name=_('Age distribution 55-64 years'), null=True)
    equity_age_dist_65_above = models.FloatField(verbose_name=_('Age distribution 55-above years'), null=True)
    procurement_annual_public_spending = models.FloatField(verbose_name=_('Annual public procurement spending'), null=True)
    procurement_gdp_pc = models.FloatField(verbose_name=_('% of Procurement to GDP'), null=True)
    procurement_covid_spending = models.FloatField(verbose_name=_('COVID-19 spending'), null=True)
    procurement_total_market_pc = models.FloatField(verbose_name=_('% from total procurement market'), null=True)
    covid19_procurement_policy = models.TextField(verbose_name=_('COVID-19 Procurement Policy'), null=True)
    covid19_preparedness = models.TextField(verbose_name=_('COVID-19 Preparedness'), null=True)

    class Meta:
        verbose_name_plural = _('Countries')

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Tender(models.Model):
    PROCUREMENT_METHOD_CHOICES = [
        ('open', 'open'),
        ('limited', 'limited'),
        ('direct', 'direct'),
        ('selective', 'selective'),
    ]

    TENDER_STATUS_CHOICES = [
        ('active', 'active'),
        ('completed', 'completed'),
        ('canceled', 'canceled'),
    ]

    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='tenders')
    project_title = models.CharField(max_length=250)
    procurement_method = models.CharField(max_length=25, choices=PROCUREMENT_METHOD_CHOICES)
    supplier_name = models.CharField(max_length=250)
    status = models.CharField(max_length=25, choices=TENDER_STATUS_CHOICES)
    value_usd = models.FloatField()

    def __str__(self):
        return self.project_title
