from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.conf.urls import url
from .models import Country, Language, Tender, Supplier, EquityCategory, EquityKeywords, Topic
from content.models import CountryPartner, DataImport

class EquityInline(admin.TabularInline):
    model = EquityKeywords

class EquityAdmin(admin.ModelAdmin):
    inlines= [
        EquityInline,
    ]



admin.site.register(Language)
admin.site.register(Topic)
admin.site.register(Supplier)
admin.site.register(EquityCategory,EquityAdmin)

@admin.register(DataImport)
class DataImportAdmin(admin.ModelAdmin):
    exclude = ('path','depth','numchild','slug','owner','go_live_at','expire_at','first_published_at','search_description','show_in_menus','seo_title','content_type')
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

    def import_status(self):
        country= str(self.country)
        # import_file = str(self.import_file).split("/")[-1]
        validated = bool(self.validated)
        data_import_id = str(self.page_ptr_id)
        if self.imported:
            return format_html(
                    f'''<a class="button" disabled="True">Imported</a>&nbsp;<img src="/static/admin/img/icon-yes.svg" alt="True">'''
                    )
        else:
            return format_html(
                f'''<a class="button" href="/data_import?country={country}&data_import_id={data_import_id}&validated={validated}">Import</a>&nbsp;'''
            )
    import_status.short_description = 'Import Status'

    list_display = ('title','description','country','validated',import_status,)

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
