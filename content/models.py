from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from django.template.defaultfilters import slugify
from django.utils.timezone import now
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from django.conf import settings
from django.core.signals import request_finished
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
import pandas as pd

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.admin.menu import MenuItem
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.api import APIField
from ckeditor.fields import RichTextField
from wagtail.core.models import Page
from wagtail.documents.models import Document
from wagtail.core.models import Orderable
from wagtail.core.templatetags import wagtailcore_tags
from wagtail.search import index
from taggit.models import TaggedItemBase, Tag as TaggitTag

from country.models import Country,Language, TempDataImportTable,ImportBatch, Topic
from .validators import validate_file_extension

class Contents(Page):
    parent_page_types = ['wagtailcore.Page']
    subpage_types = [
        'content.InsightsPage',
        'content.EventsPage',
        'content.ResourcesPage',
        'content.StaticPage',
        'content.DataImport',
    ]
class InsightsPage(Page):
    parent_page_types = ['content.Contents']
    
    subpage_types = []
    contents_choice = [
        ('News', 'News'),
        ('Blog', 'Blog'),
    ]
    contents_type = models.CharField(
        max_length=20,
        choices=contents_choice,
    )
    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))

    featured = models.BooleanField("Featured ?",choices=BOOL_CHOICES,blank=False,null=False,  default=False)
    
    country =  models.ForeignKey(Country,null=True,
        blank=False,
        on_delete=models.SET_NULL, default=1,
        related_name='+')
    published_date = models.DateField("Published date",default=now, editable=False)
    body = RichTextField()
    def rendered_body(self):
        return wagtailcore_tags.richtext(self.body)

    content_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    author = models.CharField(blank=True, max_length=250)
    tags = ClusterTaggableManager(through='content.InsightPageTag', blank=True)
    news_date = models.DateField("Published date",default=now)

    language =  models.ForeignKey(Language, on_delete=models.CASCADE,blank=False, null=False)
    topics =  models.ForeignKey(Topic, on_delete=models.CASCADE,blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('contents_type'),
        FieldPanel('featured'),
        FieldPanel('language'),
        FieldPanel('topics'),
        FieldPanel('country'),
        FieldPanel('body'),
        ImageChooserPanel('content_image'),
        FieldPanel('author', classname="full"),
        FieldPanel('tags'),
        FieldPanel('news_date'),

    ]

    api_fields = [
        APIField('contents_type'),
        APIField('featured'),
        APIField('country'),
        APIField('language'),
        APIField('topics'),
        APIField('published_date'),
        APIField('rendered_body'),
        APIField('content_image'),
        APIField('author'),
        APIField('tags'),
        APIField('news_date'),
    ]

    class Meta:  # noqa
        verbose_name = "News & Blog"
        verbose_name_plural = "News &  Blog"

    search_fields = Page.search_fields + [ 
        index.SearchField('published_date'),
    ]
    settings_panels = []
    promote_panels = []


class EventsPage(Page):
    parent_page_types = ['content.Contents']
    subpage_types = []
    event_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    description = RichTextField()

    def rendered_description(self):
        return wagtailcore_tags.richtext(self.description)

    event_date = models.DateField("Event date")
    time_from = models.TimeField("Start time")
    time_to = models.TimeField("End time", 
        null=True,
        blank=True,)
    location = models.CharField(
        max_length=100,
    )

    content_panels = Page.content_panels + [
    ImageChooserPanel('event_image'),
    FieldPanel('description'),
    FieldPanel('event_date'),
    FieldPanel('time_from'),
    FieldPanel('time_to'),
    FieldPanel('location', classname="full"),
    ]

    api_fields = [
        APIField('event_image'),
        APIField('rendered_description'),
        APIField('event_date'),
        APIField('time_from'),
        APIField('time_to'),
        APIField('location')
    ]

    class Meta:  # noqa
        verbose_name = "Event"
        verbose_name_plural = "Event"

    settings_panels = []
    promote_panels = []

class ResourcesPage(Page):
    parent_page_types = ['content.Contents']
    
    subpage_types = []

    resource_choice = [
        ('Report', 'Report'),
        ('Policy', 'Policy'),
        ('Guide', 'Guide'),
        ('Tools', 'Tools'),
        ('Training Material', 'Training Material'),
    ]

    resource_type = models.CharField(
        max_length=20,
        choices=resource_choice,
    )
    description = RichTextField()

    def rendered_description(self):
        return wagtailcore_tags.richtext(self.description)

    country =  models.ForeignKey(Country, null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+')

    document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    link = models.URLField(
        max_length=10000,null = True, blank=True)

    language = models.CharField(
        max_length=2000, null = True, blank=True
    )
    lang =  models.ForeignKey(Language, on_delete=models.CASCADE,blank=False, null=False)
    topic = models.CharField(
        max_length=2000, null = True, blank=True
    )
    topics =  models.ForeignKey(Topic, on_delete=models.CASCADE,blank=True, null=True)

    published_date = models.DateField("Published date")
    author = models.CharField(blank=True, max_length=250)
    
    content_panels = Page.content_panels + [
    FieldPanel('resource_type'),
    FieldPanel('description'),
    FieldPanel('country'),
    DocumentChooserPanel('document'),
    FieldPanel('link'),
    FieldPanel('language'),
    FieldPanel('lang'),
    FieldPanel('topic'),
    FieldPanel('topics'),
    FieldPanel('published_date'),
    FieldPanel('author', classname="full"),
    ]

    api_fields = [
        APIField('resource_type'),
        APIField('rendered_description'),
        APIField('country'),
        APIField('document'),
        APIField('link'),
        APIField('language'),
        APIField('lang'),
        APIField('topic'),
        APIField('topics'),
        APIField('published_date'),
        APIField('author')
    ]

    class Meta:  # noqa
        verbose_name = "Library"
        verbose_name_plural = "Library"

    settings_panels = []
    promote_panels = []

class InsightPageTag(TaggedItemBase):
    content_object = ParentalKey('InsightsPage', related_name='post_tags')

# @register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True

class DataImport(Page):
    parent_page_types = ['content.Contents']
    
    subpage_types = []
    
    description = models.TextField(verbose_name=_('Description'), null=False, unique=True, max_length=500000)

    import_file = models.FileField(null=True,
        blank=False,upload_to="documents", validators=[validate_file_extension])

    country =  models.ForeignKey(Country, on_delete=models.CASCADE,blank=False, null=False)
    validated = models.BooleanField(null=False, blank=True, default=False)   

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('import_file'),
        FieldPanel('country'),
    ]

    api_fields = [
        APIField('description'),
        APIField('import_file'),
        APIField('country'),
    ]
    settings_panels = []
    promote_panels = []
    preview_modes = []

    class Meta:  # noqa
        verbose_name = "Data Imports"
        verbose_name_plural = "Data Imports"



class StaticPage(Page):
    parent_page_types = ['content.Contents']
    
    subpage_types = []
    
    language =  models.ForeignKey(Language, on_delete=models.CASCADE,blank=False, null=False)
    body = RichTextField()
    BOOLEAN_OPTIONS = (
        ( 'Yes','Yes'),
        ( 'No', 'No'),
    )
    show_in_header_menu =models.CharField(
        max_length=20,
        choices=BOOLEAN_OPTIONS,
        blank=False,null=False, default= 'No'
    )
    show_in_footer_menu = models.CharField(
        max_length=20,
        choices=BOOLEAN_OPTIONS,
        blank=False,null=False, default= 'No'
    )
    def rendered_body(self):
        return wagtailcore_tags.richtext(self.body)

    content_panels = Page.content_panels + [
        FieldPanel('slug'),
        FieldPanel('body'),
        FieldPanel('language'),
        FieldPanel('show_in_header_menu'),
        FieldPanel('show_in_footer_menu'),
    ]
    settings_panels = []
    promote_panels = []
    preview_modes = []

    api_fields = [
        APIField('slug'),
        APIField('rendered_body'),
        APIField('language'),
        APIField('show_in_header_menu'),
        APIField('show_in_footer_menu'),
    ]

    class Meta:  # noqa
        verbose_name = "Static Page"
        verbose_name_plural = "Static Page"

class CountryPartner(models.Model):
    alphaSpaces = RegexValidator(r'^[a-zA-Z ]+$', 'Only letters and spaces are allowed in the Country Name')
    name = models.CharField(verbose_name=_('Name'), null=False, unique=True, max_length=50, validators=[alphaSpaces])
    description = models.TextField(verbose_name=_('Description'), null=False, unique=True, max_length=500000)
    country = models.ForeignKey(Country, on_delete=models.CASCADE,blank=False, null=False)    
    email = models.EmailField(max_length=254, blank=False, unique=True)
    website = models.URLField(max_length = 200)
    order = models.IntegerField(null=True)
    logo = models.ImageField(upload_to='country/partner/logo', height_field=None, width_field=None, max_length=100)

    class Meta:
        verbose_name_plural = _('Country Partners')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(CountryPartner, self).save(*args, **kwargs)


@receiver(post_save, sender=DataImport)
def check_column_available(sender,created ,instance, *args, **kwargs):
    if created:
        filename= instance.import_file.name
        valid_columns =valid_columns =['Contract ID','Procurement procedure code','Classification Code (CPV or other)', 'Quantity, units', 'Price per unit, including VAT', 'Tender value', 'Award value','Contract value','Contract title','Contract description','Number of bidders','Buyer','Buyer ID','Buyer address (as an object)','Supplier','Supplier ID','Supplier address','Contract Status','Contract Status Code','Link to the contract','Link to the tender','Data source']
        file_path = settings.MEDIA_ROOT+'/'+str(filename)
        ws = pd.read_excel(file_path,sheet_name='data',header=0)
        if set(valid_columns).issubset(ws.columns):
            instance.validated = True
            instance.save()


@receiver(post_save, sender=DataImport)
def store_in_temp_table(sender,created, instance, *args, **kwargs):
    if created:
        filename= instance.import_file.name
        file_path = settings.MEDIA_ROOT+'/'+str(filename)
        try:
            ws = pd.read_excel(file_path,sheet_name='data',header=0)
            country_id = Country.objects.filter(name = instance.country).values('id').get()
            new_importbatch = ImportBatch(import_type="XLS file", description="Import data of file : "+filename, country_id= country_id['id'])
            new_importbatch.save()
            importbatch_id = new_importbatch.id
            i = 0
            for row in ws.iterrows():
                new_tempdata = TempDataImportTable(contract_id = ws['Contract ID'][i],
                                                    contract_date= ws['Contract date (yyyy-mm-dd)'][i],
                                                    procurement_procedure= ws['Procurement procedure'][i],
                                                    procurement_process= ws['Procurement procedure code'][i],
                                                    goods_services=ws['Goods/Services'][i],
                                                    cpv_code_clear=ws['Classification Code (CPV or other)'][i],
                                                    quantity_units=ws['Quantity, units'][i],
                                                    ppu_including_vat=ws['Price per unit, including VAT'][i],
                                                    tender_value=ws['Tender value'][i],
                                                    award_value=ws['Award value'][i],
                                                    contract_value=ws['Contract value'][i],
                                                    contract_title=ws['Contract title'][i],
                                                    contract_description=ws['Contract description'][i],
                                                    no_of_bidders=ws['Number of bidders'][i],
                                                    buyer=ws['Buyer'][i],
                                                    buyer_id=ws['Buyer ID'][i],
                                                    buyer_address_as_an_object=ws['Buyer address (as an object)'][i],
                                                    supplier=ws['Supplier'][i],
                                                    supplier_id=ws['Supplier ID'][i],
                                                    supplier_address=ws['Supplier address'][i],
                                                    contract_status=ws['Contract Status'][i],
                                                    contract_status_code=ws['Contract Status Code'][i],
                                                    link_to_contract=ws['Link to the contract'][i],
                                                    link_to_tender=ws['Link to the tender'][i],
                                                    data_source=ws['Data source'][i],
                                                    import_batch_id=importbatch_id
                                                    )
                new_tempdata.save()
                i = i+1
        except Exception as e:
            print(e)

