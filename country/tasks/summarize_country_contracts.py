import socket

from celery import Celery
from django.db.models import Count, Max, Min, Q, Sum

from country.models import Country, OverallSummary, Tender

app = Celery()


@app.task(name="summarize_country_contracts")
def summarize_country_contracts(country_code):
    country_code = country_code.upper()
    country = Country.objects.filter(country_code_alpha_2=country_code).first()
    data = get_statistics(country)

    try:
        OverallSummary.objects.filter(country=country).first().update(statistic=data, country=country)
    except OverallSummary.DoesNotExist:
        obj = OverallSummary(statistic=data, country=country)
        obj.save()

    return "Done"


def get_statistics(country):
    data = {}
    contract_summary = (
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
            total_buyers=Count("buyer_id", distinct=True),
            total_suppliers=Count("supplier_id", distinct=True),
            time_span_max=Max("contract_date"),
            time_span_min=Min("contract_date"),
        )
    )
    red_flag_summary = (
        Tender.objects.filter(country__country_code_alpha_2=country.country_code_alpha_2)
        .exclude(red_flag=None)
        .values("id")
        .aggregate(
            total_red_flag_contracts=Count("red_flag"),
            total_amount_red_flag_contracts=Sum("contract_value_usd"),
        )
    )
    equity_summary = (
        Tender.objects.filter(country__country_code_alpha_2=country.country_code_alpha_2)
        .exclude(equity_category=None)
        .values("id")
        .aggregate(
            total_equity_contracts=Count("equity_category"),
            total_amount_equity_contracts=Sum("contract_value_usd"),
        )
    )

    if contract_summary["time_span_max"] and contract_summary["time_span_min"] is not None:
        timespan = contract_summary["time_span_max"] - contract_summary["time_span_min"]
    else:
        timespan = ""

    data["country"] = country.name
    data["total_contracts"] = contract_summary["total_contracts"]
    data["total_amount_usd"] = (
        round(contract_summary["total_usd"], 2) if contract_summary["total_usd"] is not None else 0
    )
    data["total_amount_local"] = (
        round(contract_summary["total_local"], 2) if contract_summary["total_local"] is not None else 0
    )
    data["direct_contracts"] = contract_summary["direct_contracts"]
    data["limited_contracts"] = contract_summary["limited_contracts"]
    data["open_contracts"] = contract_summary["open_contracts"]
    data["selective_contracts"] = contract_summary["selective_contracts"]
    data["not_identified_method_contracts"] = contract_summary["not_identified_method_contracts"]
    data["direct_contracts_amount"] = (
        round(contract_summary["direct_amount"], 2) if contract_summary["direct_amount"] is not None else 0
    )
    data["limited_contracts_amount"] = (
        round(contract_summary["limited_amount"], 2) if contract_summary["limited_amount"] is not None else 0
    )
    data["open_contracts_amount"] = (
        round(contract_summary["open_amount"], 2) if contract_summary["open_amount"] is not None else 0
    )
    data["selective_contracts_amount"] = (
        round(contract_summary["selective_amount"], 2) if contract_summary["selective_amount"] is not None else 0
    )
    data["not_identified_contracts_amount"] = (
        round(contract_summary["not_identified_contracts_amount"], 2)
        if contract_summary["not_identified_contracts_amount"] is not None
        else 0
    )
    data["total_buyers"] = contract_summary["total_buyers"]
    data["total_suppliers"] = contract_summary["total_suppliers"]

    data["total_red_flag_contracts"] = red_flag_summary["total_red_flag_contracts"]
    data["total_amount_red_flag_contracts"] = (
        round(red_flag_summary["total_amount_red_flag_contracts"], 2)
        if red_flag_summary["total_amount_red_flag_contracts"] is not None
        else 0
    )
    data["total_equity_contracts"] = equity_summary["total_equity_contracts"]
    data["total_amount_equity_contracts"] = (
        round(equity_summary["total_amount_equity_contracts"], 2)
        if equity_summary["total_amount_equity_contracts"] is not None
        else 0
    )
    data["time_span"] = str(timespan)[:-9]
    data["gdp_per_capita"] = country.gdp
    data["healthcare_budget"] = country.healthcare_budget
    data["percentage_of_gdp_to_healthcare_budget"] = country.healthcare_gdp_pc
    data["total_covid_cases"] = country.covid_cases_total
    data["total_active_cases"] = country.covid_active_cases
    data["total_death_cases"] = country.covid_deaths_total
    data["spending_per_covid_case"] = (
        float(data["total_amount_usd"] / data["total_covid_cases"]) if data["total_covid_cases"] != 0 else 0
    )
    data["country_data_download"] = (
        "https://" + socket.gethostbyname(socket.gethostname()) + "/media/export/" + country.name + "_summary.xlsx"
    )

    return data
