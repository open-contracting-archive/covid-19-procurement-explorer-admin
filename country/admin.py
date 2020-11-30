from django.contrib import admin
from .models import Country, Language, Tender, Supplier

admin.site.register(Language)
admin.site.register(Supplier)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    readonly_fields = (
        'covid_cases_total',
        'covid_deaths_total',
        'covid_data_last_updated',
        )


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    readonly_fields = (
        'contract_value_usd',
    )
