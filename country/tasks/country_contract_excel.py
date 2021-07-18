import os
from pathlib import Path

import xlsxwriter
from celery import Celery
from django.db.models import Sum

from country.models import Buyer, Country, GoodsServices, Supplier, Tender

app = Celery()


@app.task(name="country_contract_excel")
def country_contract_excel(country_code):
    if not country_code:
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
                    contract_usd=Sum("contract_value_usd"),
                    contract_local=Sum("contract_value_local"),
                    award_local=Sum("award_value_local"),
                    award_usd=Sum("award_value_usd"),
                    tender_local=Sum("tender_value_local"),
                    tender_usd=Sum("tender_value_usd"),
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
                    except Exception:
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
        country_name = Country.objects.filter(country_code_alpha_2=country_code).first().name
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
            Tender.objects.filter(country__country_code_alpha_2=country_code)
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
                contract_usd=Sum("contract_value_usd"),
                contract_local=Sum("contract_value_local"),
                award_local=Sum("award_value_local"),
                award_usd=Sum("award_value_usd"),
                tender_local=Sum("tender_value_local"),
                tender_usd=Sum("tender_value_usd"),
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
                except Exception:
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
