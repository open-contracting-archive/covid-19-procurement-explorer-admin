import pandas as pd
from celery import Celery
from django.conf import settings

from content.models import DataImport
from country.models import Country, ImportBatch, TempDataImportTable

app = Celery()


@app.task(name="store_in_temp_table")
def store_in_temp_table(instance_id):
    instance = DataImport.objects.get(id=instance_id)
    filename = instance.import_file.name
    valid_columns = [
        "Contract ID",
        "Procurement procedure code",
        "Classification Code (CPV or other)",
        "Quantity, units",
        "Price per unit, including VAT",
        "Tender value",
        "Award value",
        "Contract value",
        "Contract title",
        "Contract description",
        "Number of bidders",
        "Buyer",
        "Buyer ID",
        "Buyer address (as an object)",
        "Supplier",
        "Supplier ID",
        "Supplier address",
        "Contract Status",
        "Contract Status Code",
        "Link to the contract",
        "Link to the tender",
        "Data source",
    ]
    file_path = settings.MEDIA_ROOT + "/" + str(filename)
    ws = pd.read_excel(file_path, sheet_name="data", header=0, na_values=None, na_filter=False)
    ws = ws.where(ws.notnull(), None)
    if set(valid_columns).issubset(ws.columns):
        instance.validated = True
        instance.no_of_rows = len(ws)
        instance.save()

    try:
        data_import_id = instance.id
        country_id = Country.objects.filter(name=instance.country).values("id").get()
        new_importbatch = ImportBatch(
            import_type="XLS file",
            description="Import data of file : " + filename,
            country_id=country_id["id"],
            data_import_id=data_import_id,
        )
        new_importbatch.save()
        importbatch_id = new_importbatch.id
        procurement_procedure_option = [
            "Open",
            "open",
            "Limited",
            "limited",
            "Selective",
            "selective",
            "Direct",
            "direct",
        ]
        contract_status_option = [
            "Active",
            "active",
            "Cancelled",
            "cancelled",
            "Completed",
            "complete",
            "completed",
            "Terminated",
            "terminated",
        ]
        i = 0

        while i <= len(ws):
            procurement_procedure_value = str(ws["Procurement procedure code"][i]).strip().lower()
            contract_status_value = str(ws["Contract Status Code"][i]).strip().lower()

            if contract_status_value in contract_status_option:
                contract_status_lowered_value = contract_status_value.lower()
                if contract_status_lowered_value == "terminated":
                    contract_status_lowered_value = "completed"
                if contract_status_lowered_value == "complete":
                    contract_status_lowered_value = "completed"
            else:
                contract_status_lowered_value = "not_identified"

            if procurement_procedure_value in procurement_procedure_option:
                procurement_procedure__lowered_value = procurement_procedure_value.lower()
            else:
                procurement_procedure__lowered_value = "not_identified"
            try:
                nulled = pd.isnull(ws["Contract value"][i])
                if not nulled:
                    new_tempdata = TempDataImportTable(
                        contract_id=ws["Contract ID"][i],
                        contract_date=ws["Contract date (yyyy-mm-dd)"][i].date(),
                        procurement_procedure=procurement_procedure__lowered_value,
                        procurement_process=ws["Procurement procedure code"][i],
                        goods_services=ws["Goods/Services"][i],
                        cpv_code_clear=ws["Classification Code (CPV or other)"][i],
                        quantity_units=ws["Quantity, units"][i],
                        ppu_including_vat=ws["Price per unit, including VAT"][i],
                        tender_value=ws["Tender value"][i],
                        award_value=ws["Award value"][i],
                        contract_value=ws["Contract value"][i],
                        contract_title=ws["Contract title"][i],
                        contract_description=ws["Contract description"][i],
                        no_of_bidders=ws["Number of bidders"][i],
                        buyer=ws["Buyer"][i],
                        buyer_id=ws["Buyer ID"][i],
                        buyer_address_as_an_object=ws["Buyer address (as an object)"][i],
                        supplier=ws["Supplier"][i],
                        supplier_id=ws["Supplier ID"][i],
                        supplier_address=ws["Supplier address"][i],
                        contract_status=contract_status_lowered_value,
                        contract_status_code=ws["Contract Status Code"][i],
                        link_to_contract=ws["Link to the contract"][i],
                        link_to_tender=ws["Link to the tender"][i],
                        data_source=ws["Data source"][i],
                        import_batch_id=importbatch_id,
                    )
                    new_tempdata.save()
            except Exception as e:
                print(e)
                pass
            i = i + 1
    except Exception as e:
        print(e)
