from ckeditor.fields import RichTextField
from django.core.validators import RegexValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag as TaggitTag
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.api import APIField
from wagtail.core.models import Page
from wagtail.core.templatetags import wagtailcore_tags
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from country.models import Country, Language, Topic

from .validators import validate_file_extension


class Contents(Page):
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = [
        "content.InsightsPage",
        "content.EventsPage",
        "content.ResourcesPage",
        "content.StaticPage",
        "content.DataImport",
    ]


class InsightsPage(Page):
    parent_page_types = ["content.Contents"]

    subpage_types = []
    contents_choice = [
        ("News", "News"),
        ("Blog", "Blog"),
    ]
    contents_type = models.CharField(
        max_length=20,
        choices=contents_choice,
    )
    BOOL_CHOICES = ((True, "Yes"), (False, "No"))

    featured = models.CharField(
        "Featured ?", choices=BOOL_CHOICES, blank=False, null=False, default=False, max_length=15
    )

    country = models.ForeignKey(
        Country, null=True, blank=False, on_delete=models.SET_NULL, default=1, related_name="+"
    )
    published_date = models.DateField("Published date", default=now, editable=False)
    body = RichTextField()

    def rendered_body(self):
        return wagtailcore_tags.richtext(self.body)

    content_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    author = models.CharField(blank=True, max_length=250)
    tags = ClusterTaggableManager(through="content.InsightPageTag", blank=True)
    news_date = models.DateField("Published date", default=now)

    language = models.ForeignKey(Language, on_delete=models.PROTECT, blank=False, null=False)
    topics = models.ForeignKey(Topic, on_delete=models.SET_NULL, blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("contents_type"),
        FieldPanel("featured"),
        FieldPanel("language"),
        FieldPanel("topics"),
        FieldPanel("country"),
        FieldPanel("body"),
        ImageChooserPanel("content_image"),
        FieldPanel("author", classname="full"),
        FieldPanel("tags"),
        FieldPanel("news_date"),
    ]

    api_fields = [
        APIField("contents_type"),
        APIField("featured"),
        APIField("country"),
        APIField("language"),
        APIField("topics"),
        APIField("published_date"),
        APIField("rendered_body"),
        APIField("content_image"),
        APIField("author"),
        APIField("tags"),
        APIField("news_date"),
    ]

    class Meta:
        verbose_name = "News & Blog"
        verbose_name_plural = "News & Blogs"

    search_fields = Page.search_fields + [
        index.SearchField("published_date"),
    ]
    settings_panels = []
    promote_panels = []


class EventsPage(Page):
    parent_page_types = ["content.Contents"]
    subpage_types = []
    event_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    description = RichTextField()

    def rendered_description(self):
        return wagtailcore_tags.richtext(self.description)

    event_date = models.DateField("Event date")
    time_from = models.TimeField("Start time")
    time_to = models.TimeField(
        "End time",
        null=True,
        blank=True,
    )
    location = models.CharField(
        max_length=100,
    )

    organisation = models.CharField(max_length=200, null=True, blank=True)

    content_panels = Page.content_panels + [
        ImageChooserPanel("event_image"),
        FieldPanel("description"),
        FieldPanel("organisation"),
        FieldPanel("event_date"),
        FieldPanel("time_from"),
        FieldPanel("time_to"),
        FieldPanel("location", classname="full"),
    ]

    api_fields = [
        APIField("event_image"),
        APIField("rendered_description"),
        APIField("organisation"),
        APIField("event_date"),
        APIField("time_from"),
        APIField("time_to"),
        APIField("location"),
    ]

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"

    settings_panels = []
    promote_panels = []


class ResourcesPage(Page):
    parent_page_types = ["content.Contents"]

    subpage_types = []

    resource_choice = [
        ("Report", "Report"),
        ("Policy", "Policy"),
        ("Guide", "Guide"),
        ("Tools", "Tools"),
        ("Training Material", "Training Material"),
    ]

    resource_type = models.CharField(
        max_length=20,
        choices=resource_choice,
    )
    description = RichTextField()

    def rendered_description(self):
        return wagtailcore_tags.richtext(self.description)

    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    document = models.ForeignKey(
        "wagtaildocs.Document", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    link = models.URLField(max_length=10000, null=True, blank=True)

    lang = models.ForeignKey(Language, on_delete=models.PROTECT, blank=False, null=False)
    topics = models.ForeignKey(Topic, on_delete=models.SET_NULL, blank=True, null=True)

    published_date = models.DateField("Published date")
    author = models.CharField(blank=True, max_length=250)

    content_panels = Page.content_panels + [
        FieldPanel("resource_type"),
        FieldPanel("description"),
        FieldPanel("country"),
        DocumentChooserPanel("document"),
        FieldPanel("link"),
        FieldPanel("lang"),
        FieldPanel("topics"),
        FieldPanel("published_date"),
        FieldPanel("author", classname="full"),
    ]

    api_fields = [
        APIField("resource_type"),
        APIField("rendered_description"),
        APIField("country"),
        APIField("document"),
        APIField("link"),
        APIField("lang"),
        APIField("topics"),
        APIField("published_date"),
        APIField("author"),
    ]

    class Meta:
        verbose_name = "Resource"
        verbose_name_plural = "Resources"

    settings_panels = []
    promote_panels = []


class InsightPageTag(TaggedItemBase):
    content_object = ParentalKey("InsightsPage", related_name="post_tags")


# @register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True


class DataImport(Page):
    parent_page_types = ["content.Contents"]

    subpage_types = []

    description = models.TextField(verbose_name=_("Description"), null=False, max_length=500000)

    import_file = models.FileField(null=True, blank=False, upload_to="documents", validators=[validate_file_extension])

    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=False, null=False)
    validated = models.BooleanField(null=False, blank=True, default=False)
    no_of_rows = models.CharField(verbose_name=_("No of rows"), null=True, max_length=10, default=0)
    imported = models.BooleanField(null=False, blank=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
        FieldPanel("import_file"),
        FieldPanel("country"),
    ]

    api_fields = [
        APIField("description"),
        APIField("import_file"),
        APIField("country"),
    ]
    settings_panels = []
    promote_panels = []
    preview_modes = []

    def clean(self):
        super().clean()
        self.slug = ""

    class Meta:
        verbose_name = "Data Import"
        verbose_name_plural = "Data Imports"


class StaticPage(Page):
    parent_page_types = ["content.Contents"]

    subpage_types = []

    language = models.ForeignKey(Language, on_delete=models.PROTECT, blank=False, null=False)
    body = RichTextField()
    PAGE_TYPE_OPTIONS = (
        ("static_page", "Static Page"),
        ("methodology", "Methodology"),
    )
    static_content_type = models.CharField(
        "Content Type",
        max_length=100,
        choices=PAGE_TYPE_OPTIONS,
        blank=False,
        null=True,
    )
    BOOLEAN_OPTIONS = (
        ("Yes", "Yes"),
        ("No", "No"),
    )
    show_in_header_menu = models.CharField(
        max_length=20, choices=BOOLEAN_OPTIONS, blank=False, null=False, default="No"
    )
    country = models.ForeignKey(
        Country, null=True, blank=False, on_delete=models.SET_NULL, default=1, related_name="+"
    )
    show_in_footer_menu = models.CharField(
        max_length=20, choices=BOOLEAN_OPTIONS, blank=False, null=False, default="No"
    )

    def rendered_body(self):
        return wagtailcore_tags.richtext(self.body)

    content_panels = Page.content_panels + [
        FieldPanel("slug"),
        FieldPanel("body"),
        FieldPanel("static_content_type"),
        FieldPanel("language"),
        FieldPanel("country"),
        FieldPanel("show_in_header_menu"),
        FieldPanel("show_in_footer_menu"),
    ]
    settings_panels = []
    promote_panels = []
    preview_modes = []

    api_fields = [
        APIField("slug"),
        APIField("rendered_body"),
        APIField("static_content_type"),
        APIField("language"),
        APIField("country"),
        APIField("show_in_header_menu"),
        APIField("show_in_footer_menu"),
    ]

    class Meta:
        verbose_name = "Static Page"
        verbose_name_plural = "Static Pages"


class CountryPartner(models.Model):
    alphaSpaces = RegexValidator(r"^[a-zA-Z ]+$", "Only letters and spaces are allowed in the Country Name")
    name = models.CharField(verbose_name=_("Name"), null=False, unique=True, max_length=50, validators=[alphaSpaces])
    description = models.TextField(verbose_name=_("Description"), null=False, unique=True, max_length=500000)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=False, null=False)
    email = models.EmailField(max_length=254, blank=False, unique=True)
    website = models.URLField(max_length=200)
    order = models.IntegerField(null=True)
    logo = models.ImageField(upload_to="country/partner/logo", height_field=None, width_field=None, max_length=100)

    class Meta:
        verbose_name = _("Country Partner")
        verbose_name_plural = _("Country Partners")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(CountryPartner, self).save(*args, **kwargs)
