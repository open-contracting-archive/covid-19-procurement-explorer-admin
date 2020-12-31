from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField

class Country(models.Model):
    CONTINENT_CHOICES = [
        ('africa', 'Africa'),
        ('asia','Asia'),
        ('europe','Europe'),
        ('middle_east','Middle East'),
        ('north_america','North America'),
        ('south_america','South America'),
        ('oceanic','Oceanic'),
    ]

    alphaSpaces = RegexValidator(r'^[a-zA-Z ]+$', 'Only letters and spaces are allowed in the Country Name')

    slug = models.SlugField(null=True, unique=True)
    name = models.CharField(verbose_name=_('Name'), null=False, unique=True, max_length=50, validators=[alphaSpaces])
    continent = models.CharField(verbose_name=_('Continent'), max_length=25, choices=CONTINENT_CHOICES, null=True, blank=False)
    population = models.BigIntegerField(verbose_name=_('Population'),null=True, blank=True, validators=[MinValueValidator(0)])
    gdp = models.FloatField(verbose_name=_('GDP'), null=True, blank=True, validators=[MinValueValidator(0)])
    country_code = models.CharField(verbose_name=_('Country code'), max_length=10, null=False)
    country_code_alpha_2 = models.CharField(verbose_name=_('Country code alpha-2'), max_length=2, null=False)
    currency = models.CharField(verbose_name=_('Currency'), max_length=50, null=False)
    healthcare_budget = models.FloatField(verbose_name=_('Healthcare budget'),null=True, blank=True, validators=[MinValueValidator(0)])
    healthcare_gdp_pc = models.FloatField(verbose_name=_('% of GDP to healthcare'), null=True, blank=True, validators=[MinValueValidator(0),MaxValueValidator(100)])
    covid_cases_total = models.BigIntegerField(verbose_name=_('Total COVID-19 cases'), null=True, blank=True, validators=[MinValueValidator(0)])
    covid_deaths_total = models.BigIntegerField(verbose_name=_('Total deaths by Covid-19'), null=True, blank=True, validators=[MinValueValidator(0)])
    covid_data_last_updated = models.DateTimeField(null=True, blank=True)
    equity_unemployment_rate = models.FloatField(verbose_name=_('Unemployment rate'), null=True, blank=True, validators=[MinValueValidator(0),MaxValueValidator(100)])
    equity_income_avg = models.FloatField(verbose_name=_('Average income'), null=True, blank=True, validators=[MinValueValidator(0)])
    equity_gender_dist_male = models.FloatField(verbose_name=_('Gender distribution male'), null=True, blank=True, validators=[MinValueValidator(0),MaxValueValidator(100)])
    equity_gender_dist_female = models.FloatField(verbose_name=_('Gender distribution female'), null=True, blank=True, validators=[MinValueValidator(0),MaxValueValidator(100)])
    equity_age_dist_0_14 = models.BigIntegerField(verbose_name=_('Age distribution 0-14 years'), null=True, blank=True, validators=[MinValueValidator(0)])
    equity_age_dist_15_24 = models.BigIntegerField(verbose_name=_('Age distribution 15-24 years'), null=True, blank=True, validators=[MinValueValidator(0)])
    equity_age_dist_25_54 = models.BigIntegerField(verbose_name=_('Age distribution 25-54 years'), null=True, blank=True, validators=[MinValueValidator(0)])
    equity_age_dist_55_64 = models.BigIntegerField(verbose_name=_('Age distribution 55-64 years'), null=True, blank=True, validators=[MinValueValidator(0)])
    equity_age_dist_65_above = models.BigIntegerField(verbose_name=_('Age distribution 65-above years'), null=True, blank=True, validators=[MinValueValidator(0)])
    procurement_annual_public_spending = models.FloatField(verbose_name=_('Annual public procurement spending'), null=True, blank=True, validators=[MinValueValidator(0)])
    procurement_gdp_pc = models.FloatField(verbose_name=_('% of Procurement to GDP'), null=True, blank=True, validators=[MinValueValidator(0),MaxValueValidator(100)])
    procurement_covid_spending = models.FloatField(verbose_name=_('COVID-19 spending'), null=True, blank=True, validators=[MinValueValidator(0)])
    procurement_total_market_pc = models.FloatField(verbose_name=_('% from total procurement market'), null=True, blank=True, validators=[MinValueValidator(0),MaxValueValidator(100)])
    covid19_procurement_policy = models.TextField(verbose_name=_('COVID-19 Procurement Policy'), null=True, blank=True)
    covid19_preparedness = models.TextField(verbose_name=_('COVID-19 Preparedness'), null=True, blank=True)

    class Meta:
        verbose_name_plural = _('Countries')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Country, self).save(*args, **kwargs)


class Language(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class CurrencyConversionCache(models.Model):
    source_currency = models.CharField(verbose_name=_('Source currency'), max_length=50, null=True)
    dst_currency = models.CharField(verbose_name=_('Dst currency'), max_length=50, null=True)
    conversion_date = models.DateField(verbose_name=_('Conversion date'), null=True)
    conversion_rate = models.FloatField(verbose_name=_('Conversion rate'), null=True)


class Supplier(models.Model):
    supplier_id = models.CharField(verbose_name=_('Supplier ID'), max_length=50, null=False, unique=True)
    supplier_name = models.CharField(verbose_name=_('Supplier name'), max_length=250, null=True, blank=True)
    supplier_address = models.CharField(verbose_name=_('Supplier address'), max_length=250, null=True, blank=True)

    def __str__(self):
        return f'{self.supplier_id} - {self.supplier_name}'


class Buyer(models.Model):
    buyer_id = models.CharField(verbose_name=_('Buyer ID'), max_length=50, null=False, unique=True)
    buyer_name = models.CharField(verbose_name=_('Buyer name'), max_length=250, null=True, blank=True)
    buyer_address = models.CharField(verbose_name=_('Buyer address'), max_length=250, null=True, blank=True)

    def __str__(self):
        return f'{self.buyer_id} - {self.buyer_name}'

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
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='tenders', null=True, blank=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='tenders', null=True, blank=True)

    contract_id = models.CharField(verbose_name=_('Contract ID'), max_length=150, null=True)
    contract_date = models.DateField(verbose_name=_('Contract date'), null=True)
    procurement_procedure = models.CharField(verbose_name=_('Procurement procedure'), max_length=25, choices=PROCUREMENT_METHOD_CHOICES, null=True)
    status = models.CharField(verbose_name=_('Contract status'), max_length=25, choices=TENDER_STATUS_CHOICES, null=True)
    link_to_contract = models.CharField(verbose_name=_('Link to contract'), max_length=250, null=True, blank=True)
    link_to_tender = models.CharField(verbose_name=_('Link to tender'), max_length=250, null=True, blank=True)
    data_source = models.CharField(verbose_name=_('Data source'), max_length=250, null=True, blank=True)

    no_of_bidders = models.BigIntegerField(verbose_name=_('Number of Bidders'), null=True, blank=True)
    contract_title = models.TextField(verbose_name=_('Contract title'), null=True, blank=True)
    contract_value_local = models.FloatField(verbose_name=_('Contract value local'), null=True, blank=True)
    contract_value_usd = models.FloatField(verbose_name=_('Contract value USD'),null=True, blank=True)
    contract_desc = models.TextField(verbose_name=_('Contract description'), null=True, blank=True)

    equity_categories = ArrayField(models.CharField(max_length=100,null=True, blank=True), default=list, null=True)

    def __str__(self):
        return self.contract_id


class GoodsServicesCategory(models.Model):
    category_name = models.CharField(verbose_name=_('Category name'), max_length=100, null=False, unique=True)
    category_desc = models.TextField(verbose_name=_('Category description'), null=True, blank=True)

    def __str__(self):
        return self.category_name


class GoodsServices(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='goods_services', null=True)
    goods_services_category = models.ForeignKey(GoodsServicesCategory, on_delete=models.CASCADE, related_name='goods_services', null=True)
    contract = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='goods_services', null=True)

    classification_code = models.CharField(verbose_name=_('Classification code'), max_length=100, null=True, blank=True)
    no_of_bidders = models.BigIntegerField(verbose_name=_('Number of bidders'), null=True, blank=True)

    contract_title = models.TextField(verbose_name=_('Contract title'), null=True, blank=True)
    contract_desc = models.TextField(verbose_name=_('Contract description'), null=True, blank=True)

    tender_value_local = models.FloatField(verbose_name=_('Tender value local'), null=True, blank=True)
    tender_value_usd = models.FloatField(verbose_name=_('Tender value USD'),null=True, blank=True)
    award_value_local = models.FloatField(verbose_name=_('Award value local'), null=True, blank=True)
    award_value_usd = models.FloatField(verbose_name=_('Award value USD'),null=True, blank=True)
    contract_value_local = models.FloatField(verbose_name=_('Contract value local'), null=True, blank=True)
    contract_value_usd = models.FloatField(verbose_name=_('Contract value USD'),null=True, blank=True)
    
    def __str__(self):
        return f'{self.goods_services_category} - {self.contract_title}'


class CovidMonthlyActiveCases(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='covid_monthly_active_cases')
    covid_data_date = models.DateField()
    active_cases_count = models.BigIntegerField(verbose_name=_('Active cases count'), null=True, blank=True)


class EquityCategory(models.Model):
    category_name = models.CharField(verbose_name=_('Category name'), max_length=50, null=True, unique=True)

    def __str__(self):
        return self.category_name


class EquityKeywords(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='equity_keywords', null=True)
    equity_category = models.ForeignKey(EquityCategory, on_delete=models.CASCADE, related_name='equity_keywords', null=True)
    keyword = models.CharField(verbose_name=_('Keyword'), max_length=100, null=False)