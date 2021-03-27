from django.core.management.base import BaseCommand
from country.models import Country, Tender, OverallSummary
from django.db.models import Count, Sum, Q
import xlsxwriter
import socket


class Command(BaseCommand):
    help = "Generate Excel Summary!!"

    def handle(self, *args, **kwargs):
        print("Exporting!!!!!!!!")
        workbook = xlsxwriter.Workbook("media/export/overall_summary.xlsx")
        worksheet = workbook.add_worksheet()
        row = 0
        column = 0
        columns = 0
        column_names = [
            "Country",
            "Total Contracts",
            "Total Amount (USD)",
            "Total Amount (Local currency)",
            "Direct Contracts",
            "Limited Contracts",
            "Open Contracts",
            "Selective Contracts",
            "Other Method Contracts",
            "Direct Contracts Amount",
            "Limited Contracts Amount",
            "Open Contracts Amount",
            "Selective Contracts Amount",
            "Not Identified Contracts Amount",
            "Active Contracts",
            "Completed Contracts",
            "Cancelled Contracts",
            "Not Identified Contract Status",
            "Active Contracts Amount",
            "Completed Contracts Amount",
            "Cancelled Contracts Amount",
            "Not Identified Amount",
            "Country Data Download",
        ]
        for item in column_names:
            worksheet.write(row, column, item)
            column += 1

        countries = Country.objects.all().exclude(country_code_alpha_2="gl")
        for country in countries:
            columns = 0
            row += 1
            data = {}
            report = (
                Tender.objects.filter(country__country_code_alpha_2=country.country_code_alpha_2)
                .values("id")
                .aggregate(
                    total_contracts=Count("id", distinct=True),
                    total_usd=Sum("goods_services__contract_value_usd", distinct=True),
                    total_local=Sum("goods_services__contract_value_local", distinct=True),
                    direct_contracts=Count("id", distinct=True, filter=Q(procurement_procedure="direct")),
                    limited_contracts=Count("id", distinct=True, filter=Q(procurement_procedure="limited")),
                    open_contracts=Count("id", distinct=True, filter=Q(procurement_procedure="open")),
                    selective_contracts=Count("id", distinct=True, filter=Q(procurement_procedure="selective")),
                    not_identified_method_contracts=Count(
                        "id", distinct=True, filter=Q(procurement_procedure="not_identified")
                    ),
                    direct_amount=Sum(
                        "goods_services__contract_value_usd", distinct=True, filter=Q(procurement_procedure="direct")
                    ),
                    limited_amount=Sum(
                        "goods_services__contract_value_usd", distinct=True, filter=Q(procurement_procedure="limited")
                    ),
                    open_amount=Sum(
                        "goods_services__contract_value_usd", distinct=True, filter=Q(procurement_procedure="open")
                    ),
                    selective_amount=Sum(
                        "goods_services__contract_value_usd",
                        distinct=True,
                        filter=Q(procurement_procedure="selective"),
                    ),
                    not_identified_contracts_amount=Sum(
                        "goods_services__contract_value_usd",
                        distinct=True,
                        filter=Q(procurement_procedure="not_identified"),
                    ),
                    active_contracts=Count("id", distinct=True, filter=Q(status="active")),
                    completed_contracts=Count("id", distinct=True, filter=Q(status="completed")),
                    cancelled_contracts=Count("id", distinct=True, filter=Q(status="cancelled")),
                    not_identified_contracts=Count("id", distinct=True, filter=Q(status="not_identified")),
                    not_identified_contracts_sum=Sum(
                        "goods_services__contract_value_usd", distinct=True, filter=Q(status="not_identified")
                    ),
                    active_contracts_sum=Sum(
                        "goods_services__contract_value_usd", distinct=True, filter=Q(status="active")
                    ),
                    completed_contracts_sum=Sum(
                        "goods_services__contract_value_usd", distinct=True, filter=Q(status="completed")
                    ),
                    cancelled_contracts_sum=Sum(
                        "goods_services__contract_value_usd", distinct=True, filter=Q(status="cancelled")
                    ),
                )
            )
            data["country"] = country.name
            data["total_contracts"] = report["total_contracts"]
            data["total_amount_usd"] = report["total_usd"]
            data["total_amount_local"] = report["total_local"]
            data["direct_contracts"] = report["direct_contracts"]
            data["limited_contracts"] = report["limited_contracts"]
            data["open_contracts"] = report["open_contracts"]
            data["selective_contracts"] = report["selective_contracts"]
            data["not_identified_method_contracts"] = report["not_identified_method_contracts"]
            data["direct_contracts_amount"] = report["direct_amount"]
            data["limited_contracts_amount"] = report["limited_amount"]
            data["open_contracts_amount"] = report["open_amount"]
            data["selective_contracts_amount"] = report["selective_amount"]
            data["not_identified_contracts_amount"] = report["not_identified_contracts_amount"]
            data["active_contracts"] = report["active_contracts"]
            data["completed_contracts"] = report["completed_contracts"]
            data["cancelled_contracts"] = report["cancelled_contracts"]
            data["not_identified_contracts"] = report["not_identified_contracts"]
            data["active_contracts_sum"] = report["active_contracts_sum"]
            data["completed_contracts_sum"] = report["completed_contracts_sum"]
            data["cancelled_contracts_sum"] = report["cancelled_contracts_sum"]
            data["not_identified_contracts_sum"] = report["not_identified_contracts_sum"]
            data["country_data_download"] = (
                "https://"
                + socket.gethostbyname(socket.gethostname())
                + "/media/export/"
                + country.name
                + "_summary.xlsx"
            )
            for key, value in data.items():
                worksheet.write(row, columns, value)
                columns += 1

            try:
                obj, created = OverallSummary.objects.get_or_create(country=country)
                print(f"Created : {obj}, {created}")
            except Exception as e:
                print(e)
        workbook.close()
