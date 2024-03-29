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
    Tender,
    Topic,
)
from .tasks import process_currency_conversion


class EquityInline(admin.TabularInline):
    model = EquityKeywords


class EquityAdmin(admin.ModelAdmin):
    inlines = [
        EquityInline,
    ]


admin.site.register(Language)
admin.site.register(Topic)
# admin.site.register(Buyer)
# admin.site.register(Supplier)
admin.site.register(EquityCategory, EquityAdmin)


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    search_fields = ["buyer_name", "buyer_address"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    search_fields = ["supplier_name", "supplier_address"]

    def has_add_permission(self, request, obj=None):
        return False


def detail_view(items):
    field_html = ""
    for key, value in items:
        if key == "errors":
            error_list_html = ""
            if len(value) > 0:
                for error in value:
                    error_list_html += f"<li>{error}</li>"
            else:
                error_list_html = "No Errors to show."
            field_html += f"<li><strong>{key.capitalize()}</strong> : <ul>{error_list_html}</ul></li>"
            continue
        field_html += f"<li><strong>{key.capitalize()}</strong> : {value}</li>"
    return format_html(field_html)


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
        "validation",
        "import_details",
    )

    @admin.display()
    def validation(self):
        field_html = ""
        for key, value in self.validation.items():
            if key == "errors":
                error_list_html = ""
                if len(value) > 0:
                    for error in value:
                        error_list_html += f"<li>{error}</li>"
                else:
                    error_list_html = "No Errors to show."
                field_html += f"<li><strong>{key.capitalize()}</strong> : <ul>{error_list_html}</ul></li>"
                continue
            field_html += f"<li><strong>{key.capitalize()}</strong> : {value}</li>"
        return format_html(field_html)

    @admin.display()
    def import_details(self):
        field_html = ""
        for key, value in self.import_details.items():
            if key == "errors":
                error_list_html = ""
                if len(value) > 0:
                    for error in value:
                        error_list_html += f"<li>{error}</li>"
                else:
                    error_list_html = "No Errors to show."
                field_html += f"<li><strong>{key.capitalize()}</strong> : <ul>{error_list_html}</ul></li>"
                continue
            field_html += f"<li><strong>{key.capitalize()}</strong> : {value}</li>"
        return format_html(field_html)

    readonly_fields = (validation, import_details)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def custom_title(self):
        data_import_id = str(self.page_ptr_id)

        if self.validated:
            return format_html(
                """<img src="/static/admin/img/icon-yes.svg" alt="True">
                <a class="button" disabled="True" >
                Validate</a>&nbsp;"""
            )
        else:
            return format_html(
                f"""<img src="/static/admin/img/icon-no.svg" alt="False">
                <a class="button" href="/data-validate?data_import_id={data_import_id}">
                Validate</a>&nbsp;"""
            )

    custom_title.short_description = "Validation"

    def import_status(self):
        validated = bool(self.validated)
        if validated and self.imported:
            return format_html(
                """<img src="/static/admin/img/icon-yes.svg" alt="True">"""
                """<a class="button" disabled="True">Import</a>&nbsp;"""
            )
        elif not validated:
            return format_html("""<a class="button" disabled="True">Import</a>&nbsp;""")
        else:
            return format_html(
                f"""<a class="button" """
                f"""href="/data-import?country_code={str(self.country.country_code_alpha_2)}"""
                f"""&data_import_id={str(self.page_ptr_id)}"""
                f"""&validated={validated}">Import</a>&nbsp;"""
            )

    import_status.short_description = "Import Status"

    # def validate(self):
    #     data_import_id = str(self.page_ptr_id)
    #     if self.validated:
    #         return format_html(
    #             f"""<a class="button" disabled="True" href="/data_validate?data_import_id={data_import_id}">
    #             Validate</a>&nbsp;"""
    #         )
    #     else:
    #         return format_html(
    #             f"""<a class="button" onClick="this.disabled = true;"
    #              href="/data_validate?data_import_id={data_import_id}">Validate</a>&nbsp;"""
    #         )
    #
    # validate.short_description = "Validate"

    def import_actions(self):
        data_import_id = str(self.page_ptr_id)
        import_batch = ImportBatch.objects.filter(data_import_id=data_import_id).first()
        file_source = f"/media/{self.import_file}"
        if self.imported and self.validated:
            return format_html(
                f"""<a class="button" disabled="True">Edit</a>&nbsp;
                     <a class="button" href={file_source} download>Download Source File</a>&nbsp;
                     <a class="button" onclick="return confirm('Are you sure you want to delete?')"
            href="/delete-dataset?data_import_id={data_import_id}"
            id="delete">Delete</a>&nbsp;"""
            )
        else:
            return format_html(
                f"""<a class="button" href="/data-edit?data_import_id={import_batch.id if import_batch else ''}">Edit</a>&nbsp;
                <a class="button" href={file_source} download>Download Source File</a>&nbsp;
            <a class="button" onclick="return confirm('Are you sure you want to delete?')"
            href="/delete-dataset?data_import_id={data_import_id}"
            id="delete">Delete</a>&nbsp;"""
            )

    import_actions.short_description = "Actions"

    def no_of_rows(self):
        return str(self.no_of_rows)

    no_of_rows.short_description = "No. of rows"

    def import_date(self):
        return str(self.created_at.date())

    import_date.short_description = "Imported Date"

    list_display = (
        "title",
        "description",
        "country",
        no_of_rows,
        import_date,
        custom_title,
        import_status,
        import_actions,
    )


@admin.register(DataProvider)
class DataProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "website")


# @admin.register(TempDataImportTable)
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
    fields = (
        "id",
        "classification_code",
        "contract_title",
        "contract_desc",
        "tender_value_local",
        "contract_value_local",
        "award_value_local",
        "goods_services_category",
        "country",
    )


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supplier"].queryset = Supplier.objects.filter(country=self.instance.country)
        self.fields["buyer"].queryset = Buyer.objects.filter(country=self.instance.country)


class TenderAdmin(admin.ModelAdmin):
    form = TenderForm
    list_display = ("contract_id", "contract_title", "country", "contract_date")
    search_fields = ("id", "contract_id", "contract_title")
    inlines = [
        GoodsAndServicesInline,
    ]

    def save_model(self, request, obj, form, change):
        obj.from_admin_site = True  # here we setting instance attribute which we check in `post_save`
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        conversion_date = form["contract_date"].value()
        for form_set in formsets:
            if form_set.has_changed():
                for value in form_set:
                    # todo: do not fetch country object in loop
                    country_id = value["country"].value()
                    source_currency = Country.objects.get(id=country_id).currency

                    goods_services_row_id = value["id"].value()
                    process_currency_conversion.apply_async(
                        args=(goods_services_row_id, conversion_date, source_currency), queue="covid19"
                    )

        super().save_related(request, form, formsets, change)


admin.site.register(Tender, TenderAdmin)


@admin.register(RedFlag)
class RedFlagAdmin(admin.ModelAdmin):
    list_display = ("title", "implemented")

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "100"})},
    }
