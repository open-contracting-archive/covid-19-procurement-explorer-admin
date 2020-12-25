from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
)

from .models import InsightsPage, EventsPage, ResourcesPage

class InsightsPageAdmin(ModelAdmin):
    model = InsightsPage
    menu_label = 'News & Blog'  
    menu_icon = 'doc-full'  
    menu_order = 300 
    add_to_settings_menu = False  
    exclude_from_explorer = False 
    list_display = ('contents_type','title','author','country','tags','published_date')
    list_filter = ('contents_type','country','author', 'tags')
    search_fields = ('contents_type', 'body')

modeladmin_register(InsightsPageAdmin)

class EventsPageAdmin(ModelAdmin):
    model = EventsPage
    menu_label = 'Events'  
    menu_icon = 'date'  
    menu_order = 300 
    add_to_settings_menu = False  
    exclude_from_explorer = False 
    list_display = ('description','event_date','time_from','location')
    list_filter = ('event_date','location')
    search_fields = ('description')

modeladmin_register(EventsPageAdmin)

class ResourcesPageAdmin(ModelAdmin):
    model = ResourcesPage
    menu_label = 'Library'  
    menu_icon = 'folder-open-inverse'  
    menu_order = 300 
    add_to_settings_menu = False  
    exclude_from_explorer = False 
    list_display = ('resource_type','description','published_date','author')
    list_filter = ('author','country')
    search_fields = ('description')

modeladmin_register(ResourcesPageAdmin)
