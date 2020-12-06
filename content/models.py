from django.db import models
from country.models import Country
from django.utils.timezone import now

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailvideos.edit_handlers import VideoChooserPanel
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.api import APIField
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.documents.models import Document
from wagtail.core.models import Orderable
from taggit.models import TaggedItemBase, Tag as TaggitTag

class InsightsPage(Page):
    contents_choice = [
        ('News', 'News'),
        ('Blog', 'Blog'),
    ]
    contents_type = models.CharField(
        max_length=20,
        choices=contents_choice,
    )
    
    country =  models.ForeignKey(Country,null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+')
    published_date = models.DateField("Published date",default=now, editable=False)
    body = RichTextField()
    content_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    author = models.CharField(blank=True, max_length=250)
    tags = ClusterTaggableManager(through='content.InsightPageTag', blank=True)

    parent_page_type = [
        'wagtailcore.Page'  # appname.ModelName
    ]

    content_panels = Page.content_panels + [
        FieldPanel('contents_type'),
        FieldPanel('country'),
        FieldPanel('body', classname="full"),
        ImageChooserPanel('content_image'),
        FieldPanel('author', classname="full"),
        FieldPanel('tags'),
    ]

    api_fields = [
        APIField('contents_type'),
        APIField('country'),
        APIField('published_date'),
        APIField('body'),
        APIField('content_image'),
        APIField('author'),
        APIField('tags'),
    ]

    class Meta:  # noqa
        verbose_name = "Insight"
        verbose_name_plural = "Insights"


class EventsPage(Page):
    event_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    description = RichTextField()
    event_date = models.DateField("Event date")
    time_from = models.TimeField("Start time")
    time_to = models.TimeField("End time", 
        null=True,
        blank=True,)
    location = models.CharField(
        max_length=100,
    )

    parent_page_type = [
        'wagtailcore.Page'  # appname.ModelName
    ]

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
        APIField('description'),
        APIField('event_date'),
        APIField('time_from'),
        APIField('time_to'),
        APIField('location')
    ]

    class Meta:  # noqa
        verbose_name = "Event"
        verbose_name_plural = "Events"

class ResourcesPage(Page):
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
    
    parent_page_type = [
        'wagtailcore.Page'  # appname.ModelName
    ]
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
        APIField('description'),
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