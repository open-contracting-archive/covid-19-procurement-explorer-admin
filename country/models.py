from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from django.db.models import Avg, Count, Min, Sum, Window, Q, F

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
    country_code_alpha_2 = models.CharField(verbose_name=_('Country code alpha-2'), max_length=2, null=False,db_index=True)
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

class Topic(models.Model):
    title = models.CharField(
        max_length=100
    )
    slug = models.SlugField(
        default='',
        editable=False,
        max_length=100
    )

    def save(self, *args, **kwargs):
        value = self.title
        self.slug = slugify(value)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class CurrencyConversionCache(models.Model):
    source_currency = models.CharField(verbose_name=_('Source currency'), max_length=50, null=True)
    dst_currency = models.CharField(verbose_name=_('Dst currency'), max_length=50, null=True)
    conversion_date = models.DateField(verbose_name=_('Conversion date'), null=True)
    conversion_rate = models.FloatField(verbose_name=_('Conversion rate'), null=True)


class SupplierManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(amount_local=Sum('tenders__goods_services__contract_value_local'),amount_usd=Sum('tenders__goods_services__contract_value_usd'),country_name=F('tenders__country__name'),red_flag_count=Count('tenders__red_flag',distinct=True),product_category_count=Count('tenders__goods_services__goods_services_category', distinct=True),tender_count=Count('tenders__id',distinct=True),buyer_count=Count('tenders__buyer_id',filter=Q(tenders__buyer_id__isnull=False),distinct=True))


class BuyerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(amount_local=Sum('tenders__goods_services__contract_value_local'),amount_usd=Sum('tenders__goods_services__contract_value_usd'),country_name=F('tenders__country__name'),red_flag_count=Count('tenders__red_flag',distinct=True),product_category_count=Count('tenders__goods_services__goods_services_category', distinct=True),tender_count=Count('tenders__id',distinct=True),supplier_count=Count('tenders__supplier_id',filter=Q(tenders__supplier_id__isnull=False),distinct=True))

class TenderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(amount_local=Sum('goods_services__contract_value_local'),amount_usd=Sum('goods_services__contract_value_usd'),red_flag_count=Count('red_flag'),tender_count=Count('id',distinct=True))

class Supplier(models.Model):
    supplier_id = models.CharField(verbose_name=_('Supplier ID'), max_length=50, null=False, unique=True)
    supplier_name = models.CharField(verbose_name=_('Supplier name'), max_length=250, null=True, blank=True,db_index=True)
    supplier_address = models.CharField(verbose_name=_('Supplier address'), max_length=250, null=True, blank=True)
    objects = SupplierManager()

    def __str__(self):
        return f'{self.supplier_id} - {self.supplier_name}'


class Buyer(models.Model):
    buyer_id = models.CharField(verbose_name=_('Buyer ID'), max_length=50, null=False)
    buyer_name = models.CharField(verbose_name=_('Buyer name'), max_length=250, null=True, blank=True,db_index=True)
    buyer_address = models.CharField(verbose_name=_('Buyer address'), max_length=250, null=True, blank=True)
    objects = BuyerManager()

    def __str__(self):
        return f'{self.buyer_id} - {self.buyer_name}'
        

class EquityCategory(models.Model):
    category_name = models.CharField(verbose_name=_('Category name'), max_length=50, null=True, unique=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Equity Categories"


class RedFlag(models.Model):
    title = models.CharField(verbose_name=_('Red Flag Title'), max_length=250, null=True, blank=True,db_index=True)
    description = models.CharField(verbose_name=_('Description'), max_length=300, null=True, blank=True,db_index=True)
    function_name = models.CharField(verbose_name=_('Function Name'), max_length=300, null=True, blank=True,db_index=True)

    def __str__(self):
        return self.title


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
    contract_date = models.DateField(verbose_name=_('Contract date'), null=True,db_index=True)
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
    equity_category = models.ManyToManyField(EquityCategory)
    red_flag = models.ManyToManyField(RedFlag)

    def __str__(self):
        return self.contract_id


class GoodsServicesCategory(models.Model):
    category_name = models.CharField(verbose_name=_('Category name'), max_length=100, null=False, unique=True,db_index=True)
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
    contract_value_local = models.FloatField(verbose_name=_('Contract value local'), null=True, blank=True,db_index=True)
    contract_value_usd = models.FloatField(verbose_name=_('Contract value USD'),null=True, blank=True,db_index=True)
    
    def __str__(self):
        return f'{self.goods_services_category} - {self.contract_title}'


class CovidMonthlyActiveCases(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='covid_monthly_active_cases')
    covid_data_date = models.DateField()
    active_cases_count = models.BigIntegerField(verbose_name=_('Active cases count'), null=True, blank=True)
    death_count = models.BigIntegerField(verbose_name=_('Death count'), null=True, blank=True)



class EquityKeywords(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='equity_keywords', null=True)
    equity_category = models.ForeignKey(EquityCategory, on_delete=models.CASCADE, related_name='equity_keywords', null=True)
    keyword = models.CharField(verbose_name=_('Keyword'), max_length=100, null=False)


class ImportBatch(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='import_batch_country',null=True)
    import_type=models.CharField(verbose_name= ('Import Type'), max_length=150, null=False)
    description=models.CharField(verbose_name= ('Description'), max_length=500, null=False)
    data_import_id = models.IntegerField(null=True)
    def __str__(self):
        return f'Import batch id: {str(self.id)}'

class TempDataImportTable(models.Model):
    import_batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name='import_batch',null=True)
    contract_id = models.CharField(verbose_name= ('Contract Id'), max_length=1500, null=True)
    contract_date = models.CharField(verbose_name= ('Contract date'), max_length=1500, null=True)
    procurement_procedure = models.CharField(verbose_name= ('Procurement procedure'), max_length=1500, null=True)
    procurement_process = models.CharField(verbose_name= ('Procurement process'), max_length=1500, null=True)
    goods_services = models.CharField(verbose_name= ('Goods/Services'), max_length=1500, null=True)
    cpv_code_clear = models.CharField(verbose_name= ('CPV code clear'), max_length=1500, null=True)
    quantity_units = models.CharField(verbose_name= ('Quantity,units'), max_length=1500, null=True)
    ppu_including_vat = models.CharField(verbose_name= ('Price per units including VAT'), max_length=1500, null=True)
    tender_value = models.CharField(verbose_name= ('Tender value'), max_length=1500, null=True)
    award_value = models.CharField(verbose_name= ('Award value'), max_length=1500, null=True)
    contract_value = models.CharField(verbose_name= ('Contract value'), max_length=1500, null=True)
    contract_title = models.CharField(verbose_name= ('Contract title'), max_length=1500, null=True)
    contract_description = models.CharField(verbose_name= ('Award value'), max_length=1500, null=True)
    no_of_bidders = models.CharField(verbose_name= ('No of bidders'), max_length=1500, null=True)
    buyer = models.CharField(verbose_name= ('Buyer'), max_length=1500, null=True)
    buyer_id = models.CharField(verbose_name= ('Buyer ID'), max_length=150, null=True)
    buyer_address_as_an_object = models.CharField(verbose_name= ('Buyer Address(as an object)'), max_length=1500, null=True)
    supplier = models.CharField(verbose_name= ('Supplier'), max_length=1500, null=True)
    supplier_id = models.CharField(verbose_name= ('Supplier ID'), max_length=1500, null=True)
    supplier_address = models.CharField(verbose_name= ('Supplier Address'), max_length=1500, null=True)
    contract_status = models.CharField(verbose_name= ('Contract Status'), max_length=1500, null=True)
    contract_status_code = models.CharField(verbose_name= ('Contract Status Code'), max_length=1500, null=True)
    link_to_contract = models.CharField(verbose_name= ('Link to Contract'), max_length=1500, null=True)
    link_to_tender = models.CharField(verbose_name= ('Link to Tender'), max_length=1500, null=True)
    data_source = models.CharField(verbose_name= ('Data Source'), max_length=1500, null=True)

    def __str__(self):
        return self.contract_id

class DataProvider(models.Model):
    alphaSpaces = RegexValidator(r'^[a-zA-Z ]+$', 'Only letters and spaces are allowed in the Country Name')
    name = models.CharField(verbose_name=_('Name'), null=False, unique=True, max_length=50, validators=[alphaSpaces])
    country = models.ForeignKey(Country, on_delete=models.CASCADE,blank=False, null=False)    
    website = models.URLField(max_length = 200)
    logo = models.ImageField(upload_to='dataprovider/logo', height_field=None, width_field=None, max_length=100)
    remark = models.TextField(verbose_name=_('Remark'), null=False, unique=True, max_length=500000)

    class Meta:
        verbose_name_plural = _('Data Providers')

    def __str__(self):
        return self.name
