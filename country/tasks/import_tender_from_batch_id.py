import sys
import traceback

from celery import Celery
from django.core import management

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
from country.tasks import fix_contract_name_value, local_currency_to_usd
from visualization.helpers.scheduler import ScheduleRunner

app = Celery()


@app.task(name="import_tender_from_batch_id")
def import_tender_from_batch_id(batch_id, country, currency):
    print(f"import_tender_data from Batch_id {batch_id}")
    total_rows_imported_count = 0
    imported_list_id = []

    try:
        temp_data = TempDataImportTable.objects.filter(import_batch_id=batch_id)
        country = country
        currency = currency
    except Exception:
        traceback.print_exc(file=sys.stdout)
        return True

    for row in temp_data:
        try:
            print(row, "...")
            contract_id = row.contract_id
            contract_date = row.contract_date

            procurement_procedure = row.procurement_procedure.strip().lower()

            classification_code = row.cpv_code_clear
            goods_services_category_name = row.goods_services

            goods_services_category_desc = ""

            if row.tender_value:
                tender_value_local = float(row.tender_value)
            else:
                tender_value_local = 0
            if row.award_value:
                award_value_local = float(row.award_value)
            else:
                award_value_local = 0
            if row.contract_value:
                contract_value_local = float(row.contract_value)
            else:
                contract_value_local = 0

            contract_title = row.contract_title
            contract_desc = row.contract_description
            if row.no_of_bidders.isdigit():
                no_of_bidders = row.no_of_bidders
            else:
                no_of_bidders = None

            buyer_id = row.buyer_id
            buyer_name = row.buyer
            buyer_address = row.buyer_address_as_an_object

            supplier_id = row.supplier_id
            supplier_name = row.supplier
            supplier_address = row.supplier_address

            status = row.contract_status.strip().lower()
            if status == "Terminated" or status == "Canclled":
                status = "canceled"

            quantity_units = row.quantity_units
            ppu_including_vat = row.ppu_including_vat

            link_to_contract = row.link_to_contract
            link_to_tender = row.link_to_tender
            data_source = row.data_source

            # Get Country
            country_obj = Country.objects.filter(name=country).first()

            # Get or Create Supplier
            if supplier_id or supplier_name or supplier_address:
                supplier_id = str(supplier_id).strip() if supplier_id else " "
                supplier_name = str(supplier_name).strip() if supplier_name else " "
                supplier_address = str(supplier_address).strip() if supplier_address else " "
                supplier_obj = Supplier.objects.filter(
                    supplier_id__iexact=supplier_id,
                    supplier_name__iexact=supplier_name,
                    supplier_address__iexact=supplier_address,
                ).first()
                if not supplier_obj:
                    supplier_obj = Supplier(
                        supplier_id=supplier_id,
                        supplier_name=supplier_name,
                        supplier_address=supplier_address,
                        country=country_obj,
                    )
                    supplier_obj.save()
            else:
                supplier_obj = None

            # Get or Create Buyer
            if buyer_id or buyer_name or buyer_address:
                buyer_id = str(buyer_id).strip() if buyer_id else " "
                buyer_name = str(buyer_name).strip() if buyer_name else " "
                buyer_address = str(buyer_address).strip() if buyer_address else " "
                buyer_obj = Buyer.objects.filter(
                    buyer_id__iexact=buyer_id, buyer_name__iexact=buyer_name, buyer_address__iexact=buyer_address
                ).first()
                if not buyer_obj:
                    buyer_obj = Buyer(
                        buyer_id=buyer_id,
                        buyer_name=buyer_name,
                        buyer_address=buyer_address,
                        country=country_obj,
                    )
                    buyer_obj.save()
            else:
                buyer_obj = None

            # Get or Create Tender Contract
            if contract_id:
                contract_id = str(contract_id).strip()
                tender_obj = Tender.objects.filter(
                    contract_id=contract_id, contract_date=contract_date, buyer=buyer_obj
                ).first()
                if not tender_obj:
                    tender_obj = Tender(
                        country=country_obj,
                        supplier=supplier_obj,
                        buyer=buyer_obj,
                        contract_id=contract_id,
                        contract_date=contract_date,
                        procurement_procedure=procurement_procedure,
                        status=status,
                        link_to_contract=link_to_contract,
                        link_to_tender=link_to_tender,
                        data_source=data_source,
                        # for viz api compatibility only; remove these later
                        contract_title=contract_title,
                        contract_value_local=contract_value_local or None,
                        contract_desc=contract_desc,
                        no_of_bidders=no_of_bidders or None,
                        temp_table_id=row,
                    )
                    tender_obj.save()
                    imported_list_id.append(tender_obj.id)
            else:
                tender_obj = None

            # Get or Create GoodsServicesCategory
            if goods_services_category_name:
                goods_services_category_obj = GoodsServicesCategory.objects.filter(
                    category_name=goods_services_category_name
                ).first()
                if not goods_services_category_obj:
                    goods_services_category_obj = GoodsServicesCategory(
                        category_name=goods_services_category_name, category_desc=goods_services_category_desc
                    )
                    goods_services_category_obj.save()
            else:
                goods_services_category_obj = None

            # Create GoodsServices...

            if tender_obj:
                # ...only if there is a contract that it can be associated with
                goods_services_obj = GoodsServices(
                    country=country_obj,
                    goods_services_category=goods_services_category_obj,
                    contract=tender_obj,
                    supplier=supplier_obj,
                    buyer=buyer_obj,
                    classification_code=classification_code,
                    no_of_bidders=no_of_bidders or None,
                    contract_title=contract_title,
                    contract_desc=contract_desc,
                    tender_value_local=tender_value_local or 0,
                    award_value_local=award_value_local or 0,
                    contract_value_local=contract_value_local or 0,
                    quantity_units=quantity_units or None,
                    ppu_including_vat=ppu_including_vat or None,
                )
                goods_services_obj.save()
                # Execute local currency to USD conversion celery tasks
                conversion_date = contract_date
                source_currency = country_obj.currency
                source_values = {
                    "tender_value_local": tender_value_local or None,
                    "award_value_local": award_value_local or None,
                    "contract_value_local": contract_value_local or None,
                }
                goods_services_row_id = goods_services_obj.id
                local_currency_to_usd.apply_async(
                    args=(goods_services_row_id, conversion_date, source_currency, source_values), queue="covid19"
                )

            total_rows_imported_count += 1
        except Exception:
            # transaction.rollback()

            contract_id = row.contract_id
            # errors.append((index,contract_id))
            print("------------------------------")
            print(f"Error importing row, contract id {contract_id}")
            print(f"{row}\n")
            traceback.print_exc(file=sys.stdout)
            print("------------------------------")

    fix_contract_name_value(imported_list_id, country)
    instance = ScheduleRunner()
    instance.task_scheduler(
        task_name="evaluate_country_buyer",
        interval_name="every_hour",
        interval=8,
        country_alpha_code=country_obj.country_code_alpha_2,
    )
    instance.task_scheduler(
        task_name="evaluate_country_supplier",
        interval_name="every_hour",
        interval=8,
        country_alpha_code=country_obj.country_code_alpha_2,
    )
    management.call_command("export_summary_report", country_obj.country_code_alpha_2)
    data_import_id = ImportBatch.objects.get(id=batch_id).data_import_id
    DataImport.objects.filter(page_ptr_id=data_import_id).update(imported=True)
