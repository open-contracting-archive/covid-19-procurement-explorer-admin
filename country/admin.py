from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.conf.urls import url
from .models import Country, Language, Tender, Supplier
from content.models import CountryPartner, DataImport

admin.site.register(Language)
admin.site.register(Supplier)

@admin.register(DataImport)
class DataImportAdmin(admin.ModelAdmin):
    exclude = ('path','depth','numchild','slug','owner','go_live_at','expire_at','first_published_at','search_description','show_in_menus','seo_title','content_type')
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

    def import_actions(self):
        country= str(self.country)
        import_file = str(self.import_file).split("/")[-1]
        validated = bool(self.validated)
        
        return format_html(
            f'''<a class="button" href="/data_import?country={country}&filename={import_file}&validated={validated}">Import</a>&nbsp;'''
        )
    import_actions.short_description = 'Actions'
    import_actions.allow_tags = True

    # def import_status(self):
    #     country= str(self.country)
    #     import_file = str(self.import_file)
        
    #     return format_html(
    #         f'''<a class="button" href="#">Not Aprroved</a>&nbsp;'''
    #     )
    # import_status.short_description = 'Status'
    # import_status.allow_tags = True

    # def edit_status(self):
    #     country= str(self.country)
    #     import_file = str(self.import_file)
        
    #     return format_html(
    #         f'''<a class="button" href="/data_import/edit?country={country}&filename={import_file}">Edit</a>&nbsp;'''
    #     )
    # edit_status.short_description = 'Status'
    # edit_status.allow_tags = True

    list_display = ('title','description','country',import_actions,'validated')

@admin.register(CountryPartner)
class CountryPartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'country')

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    readonly_fields = (
        'covid_cases_total',
        'covid_deaths_total',
        'covid_data_last_updated',
        'slug',
        )


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    readonly_fields = (
        'contract_value_usd',
    )
