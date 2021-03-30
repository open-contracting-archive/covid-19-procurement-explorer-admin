from django import forms
from django.contrib import admin
from django.db import models
from django.forms import TextInput
from django.utils.html import format_html

from content.models import CountryPartner, DataImport

from .models import (
    Buyer,
    Country,
    DataProvider,
    EquityCategory,
    EquityKeywords,
    GoodsServices,
    ImportBatch,
    Language,
    RedFlag,
    Supplier,
    TempDataImportTable,
    Tender,
    Topic,
)


class EquityInline(admin.TabularInline):
    model = EquityKeywords


class EquityAdmin(admin.ModelAdmin):
    inlines = [
        EquityInline,
    ]


admin.site.register(Language)
admin.site.register(Topic)
admin.site.register(Buyer)
admin.site.register(Supplier)
admin.site.register(EquityCategory, EquityAdmin)


@admin.register(DataImport)
class DataImportAdmin(admin.ModelAdmin):
    exclude = (
        "path",
        "depth",
        "numchild",
        "slug",
        "owner",
        "go_live_at",
        "expire_at",
        "first_published_at",
        "search_description",
        "show_in_menus",
        "seo_title",
        "content_type",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def custom_title(self):
        title = self.validated

        if title:
            return format_html("""<img src="/static/admin/img/icon-yes.svg" alt="True">""")
        else:
            return format_html("""<img src="/static/admin/img/icon-no.svg" alt="False">""")

    custom_title.short_description = "Format validation"

    def import_status(self):
        country = str(self.country)
        # import_file = str(self.import_file).split("/")[-1]
        validated = bool(self.validated)
        data_import_id = str(self.page_ptr_id)
        if self.imported:
            return format_html(
                """<img src="/static/admin/img/icon-yes.svg" alt="True">"""
                """<a class="button" disabled="True">Imported</a>&nbsp;"""
            )
        else:
            return format_html(
                f"""<a class="button" href="/data_import?country={country}&data_import_id={data_import_id}"""
                f"""&validated={validated}">Import</a>&nbsp;"""
            )

    import_status.short_description = "Import Status"

    def validate(self):
        data_import_id = str(self.page_ptr_id)
        if self.validated:
            return format_html(
                f"""<a class="button" disabled="True" href="/data_validate?data_import_id={data_import_id}">
                Validate</a>&nbsp;"""
            )
        else:
            return format_html(
                f"""<a class="button" onClick="this.disabled = true;"
                 href="/data_validate?data_import_id={data_import_id}">Validate</a>&nbsp;"""
            )

    validate.short_description = "Validate"

    def import_actions(self):
        data_import_id = str(self.page_ptr_id)
        importbatch = ImportBatch.objects.get(data_import_id=data_import_id)
        file_source = f"/media/{self.import_file}"
        if self.imported:
            return format_html(
                f"""<a class="button" disabled="True" >Edit</a>&nbsp;
                     <a class="button" href={file_source} download>Download Source File</a>&nbsp;"""
            )
        else:
            return format_html(
                f"""<a class="button" href="/data_edit?data_import_id={importbatch.id}">Edit</a>&nbsp;
                <a class="button" href={file_source} download>Download Source File</a>&nbsp;"""
            )

    def delete(self):
        data_import_id = str(self.page_ptr_id)
        return format_html(
            f"""<a class="button" onclick="return confirm('Are you sure you want to delete?')"
            href="/delete_dataset?data_import_id={data_import_id}"
            id="delete">Delete</a>&nbsp;"""
        )

    list_display = ("title", "description", "country", custom_title, validate, import_status, import_actions, delete)


@admin.register(DataProvider)
class DataProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "website")


@admin.register(TempDataImportTable)
class TempDataImportTableAdmin(admin.ModelAdmin):
    list_editable = (
        "contract_date",
        "procurement_procedure",
        "procurement_process",
        "goods_services",
        "cpv_code_clear",
        "quantity_units",
        "ppu_including_vat",
        "tender_value",
        "award_value",
        "contract_value",
        "contract_title",
        "procurement_procedure",
        "contract_description",
        "no_of_bidders",
        "buyer",
        "buyer_id",
        "buyer_address_as_an_object",
        "supplier",
        "supplier_id",
        "supplier_address",
        "contract_status",
        "contract_status_code",
        "link_to_contract",
        "link_to_tender",
        "data_source",
    )

    list_display = (
        "contract_id",
        "contract_date",
        "procurement_procedure",
        "procurement_process",
        "goods_services",
        "cpv_code_clear",
        "quantity_units",
        "ppu_including_vat",
        "tender_value",
        "award_value",
        "contract_value",
        "contract_title",
        "procurement_procedure",
        "contract_description",
        "no_of_bidders",
        "buyer",
        "buyer_id",
        "buyer_address_as_an_object",
        "supplier",
        "supplier_id",
        "supplier_address",
        "contract_status",
        "contract_status_code",
        "link_to_contract",
        "link_to_tender",
        "data_source",
    )

    # list_filter = ('import_batch',)


@admin.register(CountryPartner)
class CountryPartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "country")


# class TenderInline(admin.TabularInline):
#     model = Tender


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    # inlines = [TenderInline,]

    readonly_fields = (
        "covid_cases_total",
        "covid_deaths_total",
        "covid_data_last_updated",
        "slug",
    )


class GoodsAndServicesInline(admin.TabularInline):
    model = GoodsServices
    extra = 0
    fields = ("classification_code", "tender_value_local", "contract_value_local", "award_value_local")


class TenderForm(forms.ModelForm):
    class Meta:
        model = Tender
        fields = (
            "country",
            "contract_title",
            "contract_desc",
            "contract_date",
            "procurement_procedure",
            "status",
            "link_to_contract",
            "no_of_bidders",
            "supplier",
            "buyer",
        )


class TenderAdmin(admin.ModelAdmin):
    readonly_fields = ("contract_value_usd",)
    form = TenderForm
    list_display = ("id", "contract_id", "contract_title")
    search_fields = ("id", "contract_id", "contract_title")
    inlines = [
        GoodsAndServicesInline,
    ]


admin.site.register(Tender, TenderAdmin)


@admin.register(RedFlag)
class RedFlagAdmin(admin.ModelAdmin):
    list_display = ("title", "implemented")

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "100"})},
    }
