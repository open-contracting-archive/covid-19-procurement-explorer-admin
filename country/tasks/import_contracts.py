import datetime
import sys
import traceback

from celery import Celery

from content.models import DataImport
from country.models import (
    Buyer,
    Country,
    GoodsServices,
    GoodsServicesCategory,
    ImportBatch,
    Supplier,
    TempDataImportTable,
    Tender,
)
from country.tasks.process_currency_conversion import process_currency_conversion
from helpers.general import close_string_mapping
from libraries.scheduler import ScheduleRunner

app = Celery()


@app.task(name="import_contracts")
def import_contracts(import_batch_id, country_code):
    import_batch = ImportBatch.objects.get(id=import_batch_id)
    data_import = DataImport.objects.get(id=import_batch.data_import_id)

    try:
        raw_data = TempDataImportTable.objects.filter(import_batch_id=import_batch_id)
    except Exception:
        traceback.print_exc(file=sys.stdout)

        return True

    country = Country.objects.filter(country_code_alpha_2=country_code).first()
    goods_service_category_mapping = get_goods_service_category_mapping()
    imported_rows = 0
    imported_contract_ids = []
    errors = []

    # Update Data Import progress ...
    # ... set status to In Progress
    data_import.import_details["status"] = "in_progress"
    data_import.import_details["started_on"] = str(datetime.datetime.now())
    data_import.save()

    for row in raw_data:
        contract_id = str(row.contract_id).strip()

        # Proceed if contract_id is valid
        if contract_id:
            try:
                contract = get_contract(row, contract_id, country)

                if not contract:
                    # Get or Create Supplier
                    supplier = get_or_create_supplier(row, country)

                    # Get or Create Buyer
                    buyer = get_or_create_buyer(row, country)

                    # Get or Create Contract
                    contract = create_contract(row, country, buyer, supplier)

                if contract:
                    # Create GoodsServices
                    goods_services_obj = create_goods_services(row, country, contract, goods_service_category_mapping)

                    # Execute local amount currency conversion to USD
                    process_currency_conversion.apply_async(
                        args=(goods_services_obj.id, row.contract_date, country.currency), queue="covid19"
                    )

                    imported_contract_ids.append(contract.id)
                imported_rows += 1
            except Exception as e:
                errors.append(f"Contract ID({contract_id}) : " + str(e))
        else:
            errors.append("Contract with no ID found")

    # Update Data Import progress ...
    # ... set status to Completed
    data_import.imported = True
    data_import.import_details["errors"] = errors
    data_import.import_details["row_count"] = imported_rows
    data_import.import_details["status"] = "completed"
    data_import.import_details["completed_on"] = str(datetime.datetime.now())
    data_import.save()

    # Run post import tasks
    run_post_process_tasks(country)

    return True


def get_goods_service_category_mapping():
    mapping = {}

    for category in GoodsServicesCategory.objects.all():
        mapped_string = close_string_mapping(category.category_name)
        mapping[mapped_string] = category

    return mapping


def get_or_create_supplier(row, country):
    supplier_id = row.supplier_id
    supplier_name = row.supplier
    supplier_address = row.supplier_address
    filter_args = {}

    if supplier_id or supplier_name or supplier_address:
        filter_args["country"] = country
        supplier_id = str(supplier_id).strip() if supplier_id else None
        supplier_name = str(supplier_name).strip() if supplier_name else None
        supplier_address = str(supplier_address).strip() if supplier_address else None

        if supplier_id:
            filter_args["supplier_id__iexact"] = supplier_id

        if supplier_name:
            filter_args["supplier_name__iexact"] = supplier_name

        if supplier_address:
            filter_args["supplier_address__iexact"] = supplier_address

        supplier = Supplier.objects.filter(**filter_args).first()

        if supplier:
            return supplier

        new_supplier = Supplier(
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            supplier_address=supplier_address,
            country=country,
        )
        new_supplier.save()

        return new_supplier
    else:
        return None


def get_or_create_buyer(row, country):
    buyer_id = row.buyer_id
    buyer_name = row.buyer
    buyer_address = row.buyer_address_as_an_object
    filter_args = {}

    if buyer_id or buyer_name or buyer_address:
        filter_args["country"] = country
        buyer_id = str(buyer_id).strip() if buyer_id else None
        buyer_name = str(buyer_name).strip() if buyer_name else None
        buyer_address = str(buyer_address).strip() if buyer_address else None

        if buyer_id:
            filter_args["buyer_id__iexact"] = buyer_id

        if buyer_name:
            filter_args["buyer_name__iexact"] = buyer_name

        if buyer_address:
            filter_args["buyer_address__iexact"] = buyer_address

        buyer = Buyer.objects.filter(**filter_args).first()

        if buyer:
            return buyer

        new_buyer = Buyer(
            buyer_id=buyer_id,
            buyer_name=buyer_name,
            buyer_address=buyer_address,
            country=country,
        )
        new_buyer.save()

        return new_buyer
    else:
        return None


def get_contract(row, contract_id, country):
    filter_args = {"contract_id": contract_id, "contract_date": row.contract_date, "country": country}
    contract = Tender.objects.filter(**filter_args).first()

    return contract if contract else None


def create_contract(row, country, buyer, supplier):
    contract_id = str(row.contract_id).strip()

    if not contract_id:
        return None

    new_contract = Tender(
        contract_id=contract_id,
        contract_title=row.contract_title,
        contract_desc=row.contract_description,
        contract_date=row.contract_date,
        no_of_bidders=row.no_of_bidders or None,
        contract_value_local=round(float(row.contract_value), 2) if row.contract_value else 0,
        procurement_procedure=row.procurement_procedure,
        status=row.contract_status,
        link_to_contract=row.link_to_contract,
        link_to_tender=row.link_to_tender,
        data_source=row.data_source,
        country=country,
        supplier=supplier,
        buyer=buyer,
        temp_table_id=row,
    )
    new_contract.save()

    return new_contract


def create_goods_services(row, country, contract, goods_service_category_mapping):
    tender_value_local = round(float(row.tender_value), 2) if row.tender_value else 0
    award_value_local = round(float(row.award_value), 2) if row.award_value else 0
    contract_value_local = round(float(row.contract_value), 2) if row.contract_value else 0
    goods_services_category_name = row.goods_services or None

    if goods_services_category_name:
        goods_services_category_name = close_string_mapping(goods_services_category_name)

        if goods_services_category_name in goods_service_category_mapping:
            goods_services_category = goods_service_category_mapping[goods_services_category_name]
        else:
            goods_services_category = goods_service_category_mapping[close_string_mapping("Not Identified")]
    else:
        goods_services_category = None

    goods_services_obj = GoodsServices(
        country=country,
        goods_services_category=goods_services_category,
        contract=contract,
        classification_code=row.cpv_code_clear,
        contract_title=row.contract_title or None,
        contract_desc=row.contract_description or None,
        tender_value_local=tender_value_local or 0,
        award_value_local=award_value_local or 0,
        contract_value_local=contract_value_local or 0,
        quantity_units=row.quantity_units or None,
        ppu_including_vat=row.ppu_including_vat or None,
    )
    goods_services_obj.save()

    return goods_services_obj


def run_post_process_tasks(country):
    instance = ScheduleRunner()
    instance.task_scheduler(
        task_name="evaluate_country_buyer",
        interval_name="every_hour",
        interval=2,
        country_alpha_code=country.country_code_alpha_2,
    )
    instance.task_scheduler(
        task_name="evaluate_country_supplier",
        interval_name="every_hour",
        interval=2,
        country_alpha_code=country.country_code_alpha_2,
    )
    instance.task_scheduler(
        task_name="summarize_country_contracts",
        interval_name="every_hour",
        interval=3,
        country_alpha_code=country.country_code_alpha_2,
    )
    instance.task_scheduler(
        task_name="country_contract_excel",
        interval_name="every_hour",
        interval=3,
        country_alpha_code=country.country_code_alpha_2,
    )
    instance.task_scheduler(
        task_name="export_summary_report",
        interval_name="every_hour",
        interval=4,
    )

    # Clear cache table
    instance.task_scheduler(
        task_name="clear_cache_table",
        interval_name="round_minute",
        interval=5,
    )
