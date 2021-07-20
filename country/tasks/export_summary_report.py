import os

import xlsxwriter
from celery import Celery

from country.models import Country, OverallSummary
from country.tasks.summarize_country_contracts import get_statistics

app = Celery()


@app.task(name="export_summary_report")
def export_summary_report():
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
        "Total cases",
        "Total active cases",
        "Total deaths",
        "$ per covid case",
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
            print(str(e))

    workbook.close()

    return "Done"
