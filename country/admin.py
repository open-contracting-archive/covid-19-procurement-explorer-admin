from django.contrib import admin
from .models import Country, Language, Tender

admin.site.register(Language)
admin.site.register(Tender)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    readonly_fields = (
        'covid_cases_total',
        'covid_deaths_total',
        'covid_data_last_updated'
        )

