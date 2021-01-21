from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from django.template.defaultfilters import slugify
from django.utils.timezone import now

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager

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
from taggit.models import TaggedItemBase, Tag as TaggitTag

from country.models import Country
class Contents(Page):
    parent_page_types = ['wagtailcore.Page']
    subpage_types = [
        'content.InsightsPage',
        'content.EventsPage',
        'content.ResourcesPage',
        'content.StaticPage',
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
    featured = models.BooleanField(blank=True,null=True)
    # template = "news_template.html"
    
    country =  models.ForeignKey(Country,null=True,
        blank=True,
        on_delete=models.SET_NULL,
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


    content_panels = Page.content_panels + [
        FieldPanel('contents_type'),
        FieldPanel('featured'),
        FieldPanel('country'),
        FieldPanel('body'),
        ImageChooserPanel('content_image'),
        FieldPanel('author', classname="full"),
        FieldPanel('tags'),
    ]

    api_fields = [
        APIField('contents_type'),
        APIField('featured'),
        APIField('country'),
        APIField('published_date'),
        APIField('rendered_body'),
        APIField('content_image'),
        APIField('author'),
        APIField('tags'),
    ]

    class Meta:  # noqa
        verbose_name = "Insight"
        verbose_name_plural = "Insights"


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
        verbose_name_plural = "Events"

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
        max_length=100)

    published_date = models.DateField("Published date")
    author = models.CharField(blank=True, max_length=250)
    
    content_panels = Page.content_panels + [
    FieldPanel('resource_type'),
    FieldPanel('description'),
    FieldPanel('country'),
    DocumentChooserPanel('document'),
    FieldPanel('link'),
    FieldPanel('published_date'),
    FieldPanel('author', classname="full"),
    ]

    api_fields = [
        APIField('resource_type'),
        APIField('rendered_description'),
        APIField('country'),
        APIField('document'),
        APIField('link'),
        APIField('published_date'),
        APIField('author')
    ]

    class Meta:  # noqa
        verbose_name = "Resource"
        verbose_name_plural = "Resources"

class InsightPageTag(TaggedItemBase):
    content_object = ParentalKey('InsightsPage', related_name='post_tags')

# @register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True

class StaticPage(Page):
    parent_page_types = ['content.Contents']
    
    subpage_types = []
    page_choice = [
        ('About Us', 'About Us'),
        ('Privacy Policy', 'Privacy Policy'),
        ('Terms Of Use', 'Terms Of Use'),
    ]
    page_type = models.CharField(
        max_length=20,
        choices=page_choice,
    )
    
    body = RichTextField()
    show_in_header_menu = models.BooleanField(blank=True,null=True)
    show_in_footer_menu = models.BooleanField(blank=True,null=True)
    def rendered_body(self):
        return wagtailcore_tags.richtext(self.body)

    content_panels = Page.content_panels + [
        FieldPanel('page_type'),
        FieldPanel('body'),
        FieldPanel('show_in_header_menu'),
        FieldPanel('show_in_footer_menu'),
    ]

    api_fields = [
        APIField('page_type'),
        APIField('rendered_body'),
        APIField('show_in_header_menu'),
        APIField('show_in_footer_menu'),
    ]

class CountryPartner(models.Model):
    alphaSpaces = RegexValidator(r'^[a-zA-Z ]+$', 'Only letters and spaces are allowed in the Country Name')
    name = models.CharField(verbose_name=_('Name'), null=False, unique=True, max_length=50, validators=[alphaSpaces])
    description = models.TextField(verbose_name=_('Description'), null=False, unique=True, max_length=500000)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)    
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