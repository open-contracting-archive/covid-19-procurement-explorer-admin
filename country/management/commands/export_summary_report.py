import os
import socket

import xlsxwriter
from django.core.management.base import BaseCommand
from django.db.models import Count, Max, Min, Q, Sum

from country.models import Country, OverallSummary, Tender


class Command(BaseCommand):
    help = "Export overall summary report"

    def add_arguments(self, parser):
        parser.add_argument("country_code", type=str, nargs="?", default=False, help="Country code")

    def handle(self, *args, **kwargs):
        self.stdout.write("Exporting")
        country_code = kwargs["country_code"] or None

        if country_code:
            country_code = country_code.upper()
            country = Country.objects.filter(country_code_alpha_2=country_code).first()
            data = get_statistics(country)
            OverallSummary.objects.filter(country=country).delete()
            OverallSummary.objects.create(statistic=data, country=country)

            return "Done"
        os.makedirs(os.path.join("media", "export"), exist_ok=True)
        workbook = xlsxwriter.Workbook("media/export/Overall Country Summary.xlsx")
        worksheet = workbook.add_worksheet()
        row = 0
        column = 0
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
            "No. of Buyers",
            "No. of Suppliers",
            "Quantity of red flags",
            "Total value of contracts with red flags",
            "Quantity of Equity Contracts",
            "Total value of equity contracts",
            "Time Span",
            "GDP per Capita",
            "Healthcare budget",
            "Percentage of GDP to healthcare budget",
            "Country Data Download",
        ]

        for item in column_names:
            worksheet.write(row, column, item)
            column += 1

        countries = Country.objects.all().exclude(country_code_alpha_2="gl")

        for country in countries:
            columns = 0
            row += 1
            data = get_statistics(country)

            for key, value in data.items():
                worksheet.write(row, columns, value)
                columns += 1

            try:
                OverallSummary.objects.filter(country=country).delete()
                OverallSummary.objects.create(statistic=data, country=country)
            except Exception as e:
                self.stderr.write(str(e))

        workbook.close()

        return "Done"


def get_statistics(country):
    data = {}
    report = (
        Tender.objects.filter(country__country_code_alpha_2=country.country_code_alpha_2)
        .values("id")
        .aggregate(
            total_contracts=Count("id", distinct=True),
            total_usd=Sum("contract_value_usd"),
            total_local=Sum("contract_value_local"),
            direct_contracts=Count("id", distinct=True, filter=Q(procurement_procedure="direct")),
            limited_contracts=Count("id", distinct=True, filter=Q(procurement_procedure="limited")),
            open_contracts=Count("id", distinct=True, filter=Q(procurement_procedure="open")),
            selective_contracts=Count("id", distinct=True, filter=Q(procurement_procedure="selective")),
            not_identified_method_contracts=Count(
                "id", distinct=True, filter=Q(procurement_procedure="not_identified")
            ),
            direct_amount=Sum("contract_value_usd", filter=Q(procurement_procedure="direct")),
            limited_amount=Sum("contract_value_usd", filter=Q(procurement_procedure="limited")),
            open_amount=Sum("contract_value_usd", filter=Q(procurement_procedure="open")),
            selective_amount=Sum(
                "contract_value_usd",
                filter=Q(procurement_procedure="selective"),
            ),
            not_identified_contracts_amount=Sum(
                "contract_value_usd",
                filter=Q(procurement_procedure="not_identified"),
            ),
            no_of_buyers=Count("buyer_id", distinct=True),
            no_of_suppliers=Count("supplier_id", distinct=True),
            time_span_max=Max("contract_date"),
            time_span_min=Min("contract_date"),
            quantity_red_flag=Count("red_flag"),
            sum_red_flag=Sum("contract_value_usd", exclude=Q(red_flag=None)),
            quantity_of_equity_contracts=Count("equity_category"),
            total_value_of_equity_contracts=Sum("contract_value_usd", exclude=Q(equity_category=None)),
        )
    )

    if report["time_span_max"] and report["time_span_min"] is not None:
        timespan = report["time_span_max"] - report["time_span_min"]
    else:
        timespan = ""
    data["country"] = country.name
    data["total_contracts"] = report["total_contracts"]
    data["total_amount_usd"] = round(report["total_usd"], 2) if report["total_usd"] is not None else 0
    data["total_amount_local"] = round(report["total_local"], 2) if report["total_local"] is not None else 0
    data["direct_contracts"] = report["direct_contracts"]
    data["limited_contracts"] = report["limited_contracts"]
    data["open_contracts"] = report["open_contracts"]
    data["selective_contracts"] = report["selective_contracts"]
    data["not_identified_method_contracts"] = report["not_identified_method_contracts"]
    data["direct_contracts_amount"] = round(report["direct_amount"], 2) if report["direct_amount"] is not None else 0
    data["limited_contracts_amount"] = (
        round(report["limited_amount"], 2) if report["limited_amount"] is not None else 0
    )
    data["open_contracts_amount"] = round(report["open_amount"], 2) if report["open_amount"] is not None else 0
    data["selective_contracts_amount"] = (
        round(report["selective_amount"], 2) if report["selective_amount"] is not None else 0
    )
    data["not_identified_contracts_amount"] = (
        round(report["not_identified_contracts_amount"], 2)
        if report["not_identified_contracts_amount"] is not None
        else 0
    )
    data["no_of_buyers"] = report["no_of_buyers"]
    data["no_of_suppliers"] = report["no_of_suppliers"]
    data["quantity_of_red_flags"] = report["quantity_red_flag"]
    data["value_of_red_flag_contracts"] = round(report["sum_red_flag"], 2) if report["sum_red_flag"] is not None else 0
    data["quantity_of_equity_contracts"] = report["quantity_of_equity_contracts"]
    data["total_value_of_equity_contracts"] = (
        round(report["total_value_of_equity_contracts"], 2)
        if report["total_value_of_equity_contracts"] is not None
        else 0
    )
    data["time_span"] = str(timespan)[:-9]
    data["gdp_per_capita"] = country.gdp
    data["healthcare_budget"] = country.healthcare_budget
    data["percentage_of_gdp_to_healthcare_budget"] = country.healthcare_gdp_pc
    data["country_data_download"] = (
        "https://" + socket.gethostbyname(socket.gethostname()) + "/media/export/" + country.name + "_summary.xlsx"
    )

    return data
