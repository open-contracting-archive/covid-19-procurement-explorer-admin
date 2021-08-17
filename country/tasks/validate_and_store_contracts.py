import datetime

import pandas as pd
from celery import Celery
from django.conf import settings

from content.models import DataImport
from country.models import ImportBatch, TempDataImportTable

app = Celery()


def has_valid_columns(columns):
    return set(get_valid_columns()).issubset(columns)


@app.task(name="validate_and_store_contracts")
def validate_and_store_contracts(data_import_id):
    data_import = DataImport.objects.get(id=data_import_id)
    data_import.validation["started_on"] = str(datetime.datetime.now())

    # Check if data already validated
    if data_import.validated:
        return True

    filename = data_import.import_file.name
    errors = []
    file_path = settings.MEDIA_ROOT + "/" + str(filename)

    try:
        ws = pd.read_excel(file_path, sheet_name="data", header=0, na_values=None, na_filter=False)
    except Exception as e:
        errors.append(str(e))
        data_import.validated = False
        data_import.no_of_rows = 0
        data_import.validation["errors"] = errors
        data_import.validation["status"] = "completed_with_errors"
        data_import.validation["completed_on"] = str(datetime.datetime.now())
        data_import.save()

        return False

    ws = ws.where(ws.notnull(), None)
    row_count = len(ws)
    data_import.no_of_rows = row_count

    if not has_valid_columns(ws.columns):
        for column in get_valid_columns():
            if column not in ws.columns:
                errors.append(f"{column} column does not exist.")

        data_import.validated = True
        data_import.validation["errors"] = errors
        data_import.validation["status"] = "completed_with_errors"
        data_import.validation["completed_on"] = str(datetime.datetime.now())
        data_import.save()

        return False

    # Store contracts
    data_import.validated = True
    data_import.validation["status"] = "in_progress"
    data_import.save()
    imported_row_count = 0

    try:
        import_batch = ImportBatch(
            import_type="XLS file",
            description="Import data of file : " + filename,
            country=data_import.country,
            data_import_id=data_import.id,
        )
        import_batch.save()
        i = 0

        while i < row_count:
            if i:
                row_number = i + 2
            else:
                row_number = i + 1

            try:
                if is_valid_contract(i, ws):
                    contract_date = validate_contract_date(ws["Contract date (yyyy-mm-dd)"][i])

                    raw_data = TempDataImportTable(
                        contract_id=ws["Contract ID"][i],
                        contract_date=contract_date,
                        procurement_procedure=sanitize_procurement_procedure(ws["Procurement procedure code"][i]),
                        procurement_process=ws["Procurement procedure code"][i],
                        goods_services=ws["Goods/Services"][i],
                        cpv_code_clear=ws["Classification Code (CPV or other)"][i],
                        quantity_units=ws["Quantity, units"][i],
                        ppu_including_vat=ws["Price per unit, including VAT"][i],
                        tender_value=round(float(ws["Tender value"][i]), 2) if ws["Tender value"][i] else 0,
                        award_value=round(float(ws["Award value"][i]), 2) if ws["Award value"][i] else 0,
                        contract_value=round(float(ws["Contract value"][i]), 2) if ws["Contract value"][i] else 0,
                        contract_title=ws["Contract title"][i],
                        contract_description=ws["Contract description"][i],
                        no_of_bidders=ws["Number of bidders"][i],
                        buyer=ws["Buyer"][i],
                        buyer_id=ws["Buyer ID"][i],
                        buyer_address_as_an_object=ws["Buyer address (as an object)"][i],
                        supplier=ws["Supplier"][i],
                        supplier_id=ws["Supplier ID"][i],
                        supplier_address=ws["Supplier address"][i],
                        contract_status=sanitize_contract_status(ws["Contract Status Code"][i]),
                        contract_status_code=ws["Contract Status Code"][i],
                        link_to_contract=ws["Link to the contract"][i],
                        link_to_tender=ws["Link to the tender"][i],
                        data_source=ws["Data source"][i],
                        import_batch_id=import_batch.id,
                    )
                    raw_data.save()
                    imported_row_count += 1
            except Exception as e:
                error_mapping = {"'str' object has no attribute 'date'": "Date not provided or invalid"}

                if str(e) in error_mapping:
                    errors.append(f"Row {row_number} : " + error_mapping[str(e)])
                else:
                    errors.append(f"Row {row_number} : " + str(e))

            i += 1
    except Exception as e:
        errors.append(str(e))

    data_import.validation["errors"] = errors
    data_import.validation["row_count"] = imported_row_count
    data_import.validation["status"] = "completed"
    data_import.validation["completed_on"] = str(datetime.datetime.now())
    data_import.save()

    return True


def validate_contract_date(date_string):
    if not date_string:
        return Exception("Invalid Date")

    if type(date_string) == str:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()

    return date_string.date()


def get_valid_columns():
    return [
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


def sanitize_contract_status(string):
    contract_status = str(string).strip().lower()

    if contract_status not in [
        "active",
        "cancelled",
        "canceled",
        "complete",
        "completed",
        "terminated",
    ]:
        return "not_identified"
    elif contract_status in ["terminated", "complete"]:
        return "completed"
    elif contract_status in ["canceled"]:
        return "cancelled"

    return contract_status


def sanitize_procurement_procedure(string):
    procurement_procedure = str(string).strip().lower()

    if procurement_procedure not in [
        "open",
        "limited",
        "selective",
        "direct",
    ]:
        return "not_identified"

    return procurement_procedure


def is_valid_contract(i, ws):
    return not pd.isnull(ws["Contract value"][i])
