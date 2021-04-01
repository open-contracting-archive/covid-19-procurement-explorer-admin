import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

import dateutil.parser

# from celery import shared_task
import pandas as pd
import requests
import xlsxwriter
from celery import Celery
from django.conf import settings
from django.db.models import Sum
from requests.exceptions import Timeout

from content.models import DataImport
from country.models import (
    Buyer,
    Country,
    CurrencyConversionCache,
    EquityCategory,
    EquityKeywords,
    GoodsServices,
    GoodsServicesCategory,
    ImportBatch,
    RedFlag,
    Supplier,
    TempDataImportTable,
    Tender,
)
from country.red_flag import RedFlags

app = Celery()


@app.task(name="fetch_covid_data")
def fetch_covid_data():
    countries = Country.objects.all()

    for country in countries:
        country_code = country.country_code

        if country_code:
            try:
                r = requests.get(f"https://covid-api.com/api/reports?iso={country_code}", timeout=20)
                if r.status_code in [200]:
                    # if country_code is invalid r.json() is {'data': []}
                    covid_data = r.json()["data"]

                    if covid_data:
                        covid_cases_total = sum([province["confirmed"] for province in covid_data])
                        covid_deaths_total = sum([province["deaths"] for province in covid_data])

                        country.covid_cases_total = covid_cases_total
                        country.covid_deaths_total = covid_deaths_total
                        country.covid_data_last_updated = datetime.now()
                        country.save()
            except Timeout:
                continue


def convert_local_to_usd(conversion_date, source_currency, source_value, dst_currency="USD"):
    if type(conversion_date) == str:
        conversion_date = dateutil.parser.parse(conversion_date).date()

    if not source_value or not source_currency or not conversion_date:
        # Missing Date: "" value has an invalid date format. It must be in YYYY-MM-DD format.
        return 0

    result = CurrencyConversionCache.objects.filter(
        conversion_date=conversion_date, source_currency=source_currency, dst_currency=dst_currency
    ).first()

    if result:
        print("Found conversion data in database")
        conversion_rate = result.conversion_rate
        return round(source_value * conversion_rate, 2)
    else:
        print("Fetching conversion data from fixer.io")
        access_key = settings.FIXER_IO_API_KEY
        try:
            r = requests.get(
                f"https://data.fixer.io/api/{conversion_date}?access_key={access_key}&base={source_currency}"
                f"&symbols={dst_currency}",
                timeout=20,
            )
            # A sample response:
            #
            # {
            #     "success": true,
            #     "timestamp": 1387929599,
            #     "historical": true,
            #     "base": "MXN",
            #     "date": "2013-12-24",
            #     "rates": {
            #         "USD": 0.076811
            #     }
            # }
            if r.status_code in [200]:
                fixer_data = r.json()
                if fixer_data["success"]:
                    conversion_rate = fixer_data["rates"][dst_currency]
                    dst_value = round(source_value * conversion_rate, 2)

                    c = CurrencyConversionCache(
                        source_currency=source_currency,
                        # source_value=source_value,
                        dst_currency=dst_currency,
                        # dst_value=dst_value,
                        conversion_date=conversion_date,
                        conversion_rate=conversion_rate,
                    )
                    c.save()

                    return dst_value
        except Timeout:
            return None


@app.task(name="import_tender_from_batch_id")
def import_tender_from_batch_id(batch_id, country, currency):
    print(f"import_tender_data from Batch_id {batch_id}")
    total_rows_imported_count = 0

    try:
        temp_data = TempDataImportTable.objects.filter(import_batch_id=batch_id)
        country = country
        currency = currency
    except:
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
            if supplier_id or supplier_name:
                supplier_id = str(supplier_id).strip() if supplier_id else " "
                supplier_name = str(supplier_name).strip() if supplier_name else " "
                supplier_obj = Supplier.objects.filter(supplier_id=supplier_id, supplier_name=supplier_name).first()
                if not supplier_obj:
                    supplier_obj = Supplier(
                        supplier_id=supplier_id,
                        supplier_name=supplier_name,
                        supplier_address=supplier_address,
                    )
                    supplier_obj.save()
            else:
                supplier_obj = None

            # Get or Create Buyer
            if buyer_id or buyer_name:
                buyer_id = str(buyer_id).strip() if buyer_id else " "
                buyer_name = str(buyer_name).strip() if buyer_name else " "
                buyer_obj = Buyer.objects.filter(buyer_id=buyer_id, buyer_name=buyer_name).first()
                if not buyer_obj:
                    buyer_obj = Buyer(
                        buyer_id=buyer_id,
                        buyer_name=buyer_name,
                        buyer_address=buyer_address,
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

                print(tender_obj.id, goods_services_obj.id)

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
        except:
            # transaction.rollback()

            contract_id = row.contract_id
            # errors.append((index,contract_id))
            print("------------------------------")
            print(f"Error importing row, contract id {contract_id}")
            print(f"{row}\n")
            traceback.print_exc(file=sys.stdout)
            print("------------------------------")

    data_import_id = ImportBatch.objects.get(id=batch_id).data_import_id
    DataImport.objects.filter(page_ptr_id=data_import_id).update(imported=True)


@app.task(name="local_currency_to_usd")
def local_currency_to_usd(goods_services_row_id, conversion_date, source_currency, source_values):
    dst_tender_value = convert_local_to_usd(
        conversion_date, source_currency, source_values["tender_value_local"], dst_currency="USD"
    )
    dst_award_value = convert_local_to_usd(
        conversion_date, source_currency, source_values["award_value_local"], dst_currency="USD"
    )
    dst_contract_value = convert_local_to_usd(
        conversion_date, source_currency, source_values["contract_value_local"], dst_currency="USD"
    )

    r = GoodsServices.objects.filter(id=goods_services_row_id).first()
    if r:
        r.tender_value_usd = dst_tender_value or None
        r.award_value_usd = dst_award_value or None
        r.contract_value_usd = dst_contract_value or None
        r.save()


@app.task(name="fetch_equity_data")
def fetch_equity_data(country):
    country_instance = Country.objects.get(name=country)
    tenders = Tender.objects.filter(country=country_instance)
    keywords = EquityKeywords.objects.filter(country=country_instance)
    for tender in tenders:
        goodservices = tender.goods_services.filter(country=country_instance)
        for good_service in goodservices:
            print(good_service.id)
            for keyword in keywords:
                keyword_value = keyword.keyword
                if (
                    keyword_value in good_service.contract_title.strip()
                    or keyword_value in good_service.contract_desc.strip()
                ):
                    category = keyword.equity_category.category_name
                    print(category)
                    instance = EquityCategory.objects.get(category_name=category)
                    tender.equity_category.add(instance)


@app.task(name="process_currency_conversion")
def process_currency_conversion(
    tender_value_local, award_value_local, contract_value_local, tender_date, currency, id
):
    tender_value_usd = (
        convert_local_to_usd(source_value=tender_value_local, conversion_date=tender_date, source_currency=currency)
        if tender_value_local
        else None
    )
    award_value_usd = (
        convert_local_to_usd(source_value=award_value_local, conversion_date=tender_date, source_currency=currency)
        if award_value_local
        else None
    )
    contract_value_usd = (
        convert_local_to_usd(source_value=contract_value_local, conversion_date=tender_date, source_currency=currency)
        if contract_value_local
        else None
    )
    print(f"started processing... {id}: {tender_value_usd}, {award_value_usd}, {contract_value_usd}")
    if tender_value_usd or award_value_usd or contract_value_usd:
        tender = GoodsServices.objects.get(id=id)
        tender.tender_value_usd = tender_value_usd
        tender.award_value_usd = award_value_usd
        tender.contract_value_usd = contract_value_usd
        tender.save()
        print("Converted goodsservices id:" + str(tender.id))
    print(f"end of {id}")


@app.task(name="process_redflag")
def process_redflag(id):
    tender = Tender.objects.get(id=id)
    red_flag = RedFlags()
    flag1 = getattr(red_flag, "flag1")(id)
    flag4 = getattr(red_flag, "flag4")(id)
    flag8 = getattr(red_flag, "flag8")(id)
    if flag1:
        flag1_obj = RedFlag.objects.get(function_name="flag1")
        tender.red_flag.add(flag1_obj)
    if flag4:
        flag4_obj = RedFlag.objects.get(function_name="flag4")
        tender.red_flag.add(flag4_obj)
    if flag8:
        flag8_obj = RedFlag.objects.get(function_name="flag8")
        tender.red_flag.add(flag8_obj)
    print(f"end of {id}")


@app.task(name="clear_redflag")
def clear_redflag(id):
    tender = Tender.objects.get(id=id)
    tender.red_flag.clear()
    print(f"end of {id}")


@app.task(name="process_red_flag7")
def process_redflag7(id, tender):
    flag7_obj = RedFlag.objects.get(function_name="flag7")
    concentration = Tender.objects.filter(
        buyer__buyer_name=tender["buyer__buyer_name"], supplier__supplier_name=tender["supplier__supplier_name"]
    )
    # supplier who has signed X(10) percent or more of their contracts with the same buyer
    # (wins tenders from the same buyer)
    if len(concentration) > 10:
        for i in concentration:
            obj = Tender.objects.get(id=i.id)
            obj.red_flag.add(flag7_obj)


@app.task(name="process_red_flag6")
def process_redflag6(id, tender):
    flag6_obj = RedFlag.objects.get(function_name="flag6")
    a = (
        Tender.objects.values("buyer__buyer_name")
        .filter(
            supplier__supplier_name=tender["supplier__supplier_name"],
            supplier__supplier_address=tender["supplier__supplier_address"],
        )
        .distinct("buyer__buyer_name")
    )
    if len(a) > 2:
        if a[0]["buyer__buyer_name"] == a[1]["buyer__buyer_name"]:
            for obj in a:
                objs = Tender.objects.get(id=obj.id)
                objs.red_flag.add(flag6_obj)


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


@app.task(name="country_contract_excel")
def country_contract_excel(country):
    if not country:
        countries = Country.objects.all().exclude(country_code_alpha_2="gl")
        for country in countries:
            country_name = country.name
            file_path = f"media/export/{country_name}_summary.xlsx"
            if not os.path.exists(file_path):
                Path(file_path).touch()

            workbook = xlsxwriter.Workbook(file_path)
            worksheet = workbook.add_worksheet()
            row = 0
            column = 0
            column_names = [
                "Contract ID",
                "Contract Date",
                "Procurement Procedure",
                "Status",
                "No of bidders",
                "Contract title",
                "Contract description",
                "Buyer ID",
                "Buyer Name",
                "Buyer Address",
                "Supplier ID",
                "Supplier Name",
                "Supplier Address",
                "Contract value (USD)",
                "Contract value (local)",
                "Award value (USD)",
                "Award value (local)",
                "Tender value (USD)",
                "Tender value (local)",
                "Product Category",
                "Equity Category",
                "Link to Contract",
                "Link to tender",
                "Data Source",
            ]
            for item in column_names:
                worksheet.write(row, column, item)
                column += 1

            # Data exporting start here
            print(f"Contract Excel Exporting of {country_name} has started")

            data = {}
            reports = (
                Tender.objects.filter(country__country_code_alpha_2=country.country_code_alpha_2)
                .values(
                    "id",
                    "contract_id",
                    "contract_date",
                    "procurement_procedure",
                    "status",
                    "link_to_contract",
                    "link_to_tender",
                    "data_source",
                    "no_of_bidders",
                    "contract_title",
                    "equity_category",
                    "contract_desc",
                    "buyer_id",
                    "supplier_id",
                    "goods_services__goods_services_category__category_name",
                )
                .annotate(
                    contract_usd=Sum("goods_services__contract_value_usd"),
                    contract_local=Sum("goods_services__contract_value_local"),
                    award_local=Sum("goods_services__award_value_local"),
                    award_usd=Sum("goods_services__award_value_usd"),
                    tender_local=Sum("goods_services__tender_value_local"),
                    tender_usd=Sum("goods_services__tender_value_usd"),
                )
            )
            if reports:
                for report in reports:
                    buyer = (
                        Buyer.objects.filter(id=report["buyer_id"])
                        .values("buyer_id", "buyer_name", "buyer_address")
                        .first()
                    )
                    buyer_id = buyer["buyer_id"] if (buyer) else ""
                    buyer_name = buyer["buyer_name"] if (buyer) else ""
                    buyer_address = buyer["buyer_address"] if (buyer) else ""

                    supplier = (
                        Supplier.objects.filter(id=report["supplier_id"])
                        .values("supplier_id", "supplier_name", "supplier_address")
                        .first()
                    )
                    supplier_id = supplier["supplier_id"] if (supplier) else ""
                    supplier_name = supplier["supplier_name"] if (supplier) else ""
                    supplier_address = supplier["supplier_address"] if (supplier) else ""

                    productcategories = GoodsServices.objects.filter(contract_id=report["id"]).values(
                        "goods_services_category__category_name"
                    )
                    product_categorylist = []
                    equity_categorylist = []

                    try:
                        equitycategories = report.equity_category.all()

                        for category in equitycategories:
                            equity_categorylist.append(category.category_name)
                        equitycategories = str(",".join(set(equity_categorylist)))
                    except:
                        equity_categorylist = []
                        equitycategories = ""

                    for category in productcategories:
                        product_categorylist.append(category["goods_services_category__category_name"])

                    try:
                        data["contract_id"] = report["contract_id"]
                        data["contract_date"] = str(report["contract_date"])
                        data["procurement_procedure"] = report["procurement_procedure"]
                        data["data_source"] = report["data_source"]
                        data["no_of_bidders"] = report["no_of_bidders"]
                        data["contract_title"] = report["contract_title"]
                        data["contract_desc"] = report["contract_desc"]
                        data["buyer_id"] = buyer_id
                        data["buyer_name"] = buyer_name
                        data["buyer_address"] = buyer_address
                        data["supplier_id"] = supplier_id
                        data["supplier_name"] = supplier_name
                        data["supplier_address"] = supplier_address
                        data["contract_value_usd"] = report["contract_usd"]
                        data["contract_value_local"] = report["contract_local"]
                        data["award_value_usd"] = report["award_usd"]
                        data["award_value_local"] = report["award_local"]
                        data["tender_value_usd"] = report["tender_usd"]
                        data["tender_value_local"] = report["tender_local"]
                        data["product_categories"] = str(",".join(set(product_categorylist)))
                        data["equity_categories"] = equitycategories
                        data["status"] = report["status"]
                        data["link_to_contract"] = report["link_to_contract"]
                        data["link_to_tender"] = report["link_to_tender"]

                        row += 1
                        columns = 0
                        for key, value in data.items():
                            value = value if value else " "
                            if value is None:
                                value = ""
                            worksheet.write(row, columns, value)
                            columns += 1
                    except Exception as e:
                        print(e)
                print(f"Contract Excel Exporting of {country_name} has been successful with {row} no of rows")
            else:
                print(f"{country_name} doesnt have data")

            workbook.close()
            print("............")

    else:
        country_name = Country.objects.filter(country_code_alpha_2=country).first().name
        file_path = f"media/export/{country_name}_summary.xlsx"
        if not os.path.exists(file_path):
            Path(file_path).touch()

        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet()
        row = 0
        column = 0
        column_names = [
            "Contract ID",
            "Contract Date",
            "Procurement Procedure",
            "Status",
            "No of bidders",
            "Contract title",
            "Contract description",
            "Buyer ID",
            "Buyer Name",
            "Buyer Address",
            "Supplier ID",
            "Supplier Name",
            "Supplier Address",
            "Contract value (USD)",
            "Contract value (local)",
            "Award value (USD)",
            "Award value (local)",
            "Tender value (USD)",
            "Tender value (local)",
            "Product Category",
            "Equity Category",
            "Link to Contract",
            "Link to tender",
            "Data Source",
        ]
        for item in column_names:
            worksheet.write(row, column, item)
            column += 1

        # Data exporting start here
        print(f"Contract Excel Exporting of {country_name} has started")

        data = {}
        reports = (
            Tender.objects.filter(country__country_code_alpha_2=country)
            .values(
                "id",
                "contract_id",
                "contract_date",
                "procurement_procedure",
                "status",
                "link_to_contract",
                "link_to_tender",
                "data_source",
                "no_of_bidders",
                "contract_title",
                "contract_desc",
                "buyer_id",
                "supplier_id",
                "goods_services__goods_services_category__category_name",
            )
            .annotate(
                contract_usd=Sum("goods_services__contract_value_usd"),
                contract_local=Sum("goods_services__contract_value_local"),
                award_local=Sum("goods_services__award_value_local"),
                award_usd=Sum("goods_services__award_value_usd"),
                tender_local=Sum("goods_services__tender_value_local"),
                tender_usd=Sum("goods_services__tender_value_usd"),
            )
        )

        if reports:
            for report in reports:
                buyer = (
                    Buyer.objects.filter(id=report["buyer_id"])
                    .values("buyer_id", "buyer_name", "buyer_address")
                    .first()
                )
                buyer_id = buyer["buyer_id"] if (buyer) else ""
                buyer_name = buyer["buyer_name"] if (buyer) else ""
                buyer_address = buyer["buyer_address"] if (buyer) else ""

                supplier = (
                    Supplier.objects.filter(id=report["supplier_id"])
                    .values("supplier_id", "supplier_name", "supplier_address")
                    .first()
                )
                supplier_id = supplier["supplier_id"] if (supplier) else ""
                supplier_name = supplier["supplier_name"] if (supplier) else ""
                supplier_address = supplier["supplier_address"] if (supplier) else ""

                productcategories = GoodsServices.objects.filter(contract_id=report["id"]).values(
                    "goods_services_category__category_name"
                )
                product_categorylist = []
                equity_categorylist = []

                try:
                    equitycategories = Tender.objects.filter(id=report["id"]).values("equity_category__category_name")
                    for category in equitycategories:
                        equity_categorylist.append(category["equity_category__category_name"])
                    equitycategories = str(",".join(set(equity_categorylist)))
                except:
                    equity_categorylist = []
                    equitycategories = ""

                for category in productcategories:
                    product_categorylist.append(category["goods_services_category__category_name"])

                try:
                    data["contract_id"] = report["contract_id"]
                    data["contract_date"] = str(report["contract_date"])
                    data["procurement_procedure"] = report["procurement_procedure"]
                    data["status"] = report["status"]
                    data["no_of_bidders"] = report["no_of_bidders"]
                    data["contract_title"] = report["contract_title"]
                    data["contract_desc"] = report["contract_desc"]
                    data["buyer_id"] = buyer_id
                    data["buyer_name"] = buyer_name
                    data["buyer_address"] = buyer_address
                    data["supplier_id"] = supplier_id
                    data["supplier_name"] = supplier_name
                    data["supplier_address"] = supplier_address
                    data["contract_value_usd"] = report["contract_usd"]
                    data["contract_value_local"] = report["contract_local"]
                    data["award_value_usd"] = report["award_usd"]
                    data["award_value_local"] = report["award_local"]
                    data["tender_value_usd"] = report["tender_usd"]
                    data["tender_value_local"] = report["tender_local"]
                    data["product_categories"] = str(",".join(set(product_categorylist)))
                    data["equity_categories"] = equitycategories
                    data["link_to_contract"] = report["link_to_contract"]
                    data["link_to_tender"] = report["link_to_tender"]
                    data["data_source"] = report["data_source"]

                    row += 1
                    columns = 0
                    for key, value in data.items():
                        value = value if value else " "
                        if value is None:
                            value = ""
                        worksheet.write(row, columns, value)
                        columns += 1
                except Exception as e:
                    print(e)
            print(f"Contract Excel Exporting of {country_name} has been successful with {row} no of rows")
        else:
            print(f"{country_name} doesnt have data")

        workbook.close()
        print("............")
