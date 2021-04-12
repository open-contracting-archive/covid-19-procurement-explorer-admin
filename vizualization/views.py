import datetime
import itertools
from collections import defaultdict

import dateutil.relativedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from content.models import CountryPartner, EventsPage, InsightsPage, StaticPage
from country.models import (
    Buyer,
    Country,
    CovidMonthlyActiveCases,
    DataProvider,
    EquityCategory,
    GoodsServices,
    GoodsServicesCategory,
    RedFlag,
    Supplier,
    Tender,
)


def add_filter_args(filter_type, filter_value, filter_args):
    if filter_value != "notnull":
        filter_args[f"{filter_type}__id"] = filter_value
    else:
        filter_args[f"{filter_type}__isnull"] = False
    return filter_args


class TotalSpendingsView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        """
        Return a list of all contracts.
        """

        # Calculating total tender
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        supplier = self.request.GET.get("supplier")

        filter_args = {}
        exclude_args = {}
        exclude_args["status"] = "canceled"
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)

        total_country_tender_amount = (
            Tender.objects.filter(**filter_args)
            .exclude(**exclude_args)
            .aggregate(
                usd=Sum("goods_services__contract_value_usd"), local=Sum("goods_services__contract_value_local")
            )
        )

        bar_chart = (
            Tender.objects.filter(**filter_args)
            .exclude(**exclude_args)
            .values("procurement_procedure")
            .annotate(usd=Sum("goods_services__contract_value_usd"), local=Sum("goods_services__contract_value_local"))
        )
        selective_sum_local = 0
        limited_sum_local = 0
        open_sum_local = 0
        direct_sum_local = 0
        limited_total = 0
        open_total = 0
        selective_total = 0
        direct_total = 0
        not_identified_total = 0
        not_identified_sum_local = 0

        for i in bar_chart:
            if i["procurement_procedure"] == "selective":
                selective_total = i["usd"]
                selective_sum_local = i["local"]
            elif i["procurement_procedure"] == "limited":
                limited_total = i["usd"]
                limited_sum_local = i["local"]
            elif i["procurement_procedure"] == "open":
                open_total = i["usd"]
                open_sum_local = i["local"]
            elif i["procurement_procedure"] == "direct":
                direct_total = i["usd"]
                direct_sum_local = i["local"]
            elif i["procurement_procedure"] == "not_identified":
                not_identified_total = i["usd"]
                not_identified_sum_local = i["local"]

        line_chart = (
            Tender.objects.filter(**filter_args)
            .exclude(**exclude_args)
            .annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(usd=Sum("goods_services__contract_value_usd"), local=Sum("goods_services__contract_value_local"))
            .order_by("-month")
        )
        line_chart_local_list = [{"date": i["month"], "value": i["local"]} for i in line_chart]
        line_chart_list = [{"date": i["month"], "value": i["usd"]} for i in line_chart]

        result = {
            "usd": {
                "total": total_country_tender_amount["usd"],
                "line_chart": line_chart_list,
                "bar_chart": [
                    {"method": "open", "value": open_total},
                    {"method": "limited", "value": limited_total},
                    {"method": "selective", "value": selective_total},
                    {"method": "direct", "value": direct_total},
                    {"method": "not_identified", "value": not_identified_total},
                ],
            },
            "local": {
                "total": total_country_tender_amount["local"],
                "line_chart": line_chart_local_list,
                "bar_chart": [
                    {"method": "open", "value": open_sum_local},
                    {"method": "limited", "value": limited_sum_local},
                    {"method": "selective", "value": selective_sum_local},
                    {"method": "direct", "value": direct_sum_local},
                    {"method": "not_identified", "value": not_identified_sum_local},
                ],
            },
        }
        return JsonResponse(result)


class TotalContractsView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        """
        Return a list of all contracts.
        """
        # Calculating total tender
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        supplier = self.request.GET.get("supplier")

        open_count = 0
        selective_count = 0
        direct_count = 0
        limited_count = 0
        not_identified_count = 0
        filter_args = {}
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)

        total_country_tender = Tender.objects.filter(**filter_args).count()
        bar_chart = (
            Tender.objects.filter(**filter_args)
            .values("procurement_procedure")
            .annotate(count=Count("procurement_procedure"))
        )
        for i in bar_chart:
            if i["procurement_procedure"] == "selective":
                selective_count = i["count"]
            elif i["procurement_procedure"] == "limited":
                limited_count = i["count"]
            elif i["procurement_procedure"] == "open":
                open_count = i["count"]
            elif i["procurement_procedure"] == "direct":
                direct_count = i["count"]
            elif i["procurement_procedure"] == "not_identified":
                not_identified_count = i["count"]

        line_chart = (
            Tender.objects.filter(**filter_args)
            .annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("-month")
        )
        line_chart_list = [{"date": i["month"], "value": i["total"]} for i in line_chart]
        result = {
            "total": total_country_tender,
            "line_chart": line_chart_list,
            "bar_chart": [
                {"method": "open", "value": open_count},
                {"method": "limited", "value": limited_count},
                {"method": "selective", "value": selective_count},
                {"method": "direct", "value": direct_count},
                {"method": "not_identified", "value": not_identified_count},
            ],
        }
        return JsonResponse(result)


class AverageBidsView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        """
        Returns average bids for contracts
        """
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")

        filter_args = {}
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)

        # Month wise average of number of bids for contracts
        monthwise_data_count = (
            Tender.objects.filter(**filter_args)
            .annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("-month")
        )
        monthwise_data_sum = (
            Tender.objects.filter(**filter_args)
            .annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(sum=Sum("goods_services__no_of_bidders"))
            .order_by("-month")
        )
        final_line_chart_data = [
            {
                "date": monthwise_data_sum[i]["month"],
                "value": round(monthwise_data_sum[i]["sum"] / monthwise_data_count[i]["count"])
                if monthwise_data_sum[i]["sum"]
                else 0,
            }
            for i in range(len(monthwise_data_sum))
        ]

        # Difference percentage calculation

        # Overall average number of bids for contracts
        overall_avg = Tender.objects.filter(**filter_args).aggregate(sum=Sum("goods_services__no_of_bidders"))
        overall_avg_count = Tender.objects.filter(**filter_args).count()
        result = {
            "average": round(overall_avg["sum"] / overall_avg_count) if overall_avg["sum"] else 0,
            "line_chart": final_line_chart_data,
        }
        return JsonResponse(result)


class GlobalOverView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        temp = {}
        tender_temp = {}
        data = []
        count = (
            Tender.objects.annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(total_contract=Count("id"), total_amount=Sum("goods_services__contract_value_usd"))
            .order_by("month")
        )
        countries = Country.objects.all().exclude(country_code_alpha_2="gl")
        for i in count:
            result = {}
            end_date = i["month"] + dateutil.relativedelta.relativedelta(months=1)
            start_date = i["month"]
            result["details"] = []
            result["month"] = str(start_date.year) + "-" + str(start_date.month)
            for j in countries:
                b = {}
                tender_count = Tender.objects.filter(
                    country__country_code_alpha_2=j.country_code_alpha_2,
                    contract_date__gte=start_date,
                    contract_date__lte=end_date,
                ).count()
                tender = Tender.objects.filter(
                    country__country_code_alpha_2=j.country_code_alpha_2,
                    contract_date__gte=start_date,
                    contract_date__lte=end_date,
                ).aggregate(Sum("goods_services__contract_value_usd"))
                b["country"] = j.name
                b["country_code"] = j.country_code_alpha_2
                b["country_continent"] = j.continent
                if tender["goods_services__contract_value_usd__sum"] is None:
                    tender_val = 0
                else:
                    tender_val = tender["goods_services__contract_value_usd__sum"]
                if tender_count is None:
                    contract_val = 0
                else:
                    contract_val = tender_count
                if bool(temp) and j.name in temp.keys():
                    current_val = temp[j.name]
                    cum_value = current_val + tender_val
                    temp[j.name] = cum_value
                    b["amount_usd"] = cum_value
                else:
                    temp[j.name] = tender_val
                    b["amount_usd"] = tender_val
                if bool(tender_temp) and j.name in tender_temp.keys():
                    current_val = tender_temp[j.name]
                    cum_value = current_val + contract_val
                    tender_temp[j.name] = cum_value
                    b["tender_count"] = cum_value
                else:
                    tender_temp[j.name] = contract_val
                    b["tender_count"] = contract_val
                result["details"].append(b)
            data.append(result)
        return JsonResponse({"result": data})


class TopSuppliers(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        filter_args = {}
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        filter_args["supplier__isnull"] = False
        filter_args["goods_services__contract_value_usd__isnull"] = False
        for_value = (
            Tender.objects.filter(**filter_args)
            .values("supplier__id", "supplier__supplier_name", "country__currency")
            .annotate(
                count=Count("id"),
                usd=Sum("goods_services__contract_value_usd"),
                local=Sum("goods_services__contract_value_local"),
            )
            .exclude(usd__isnull=True)
            .order_by("-usd")[:10]
        )
        for_number = (
            Tender.objects.filter(**filter_args)
            .exclude(goods_services__contract_value_usd__isnull=True)
            .values("supplier__id", "supplier__supplier_name", "country__currency")
            .annotate(
                count=Count("goods_services__contract__id", distinct=True),
                usd=Sum("goods_services__contract_value_usd"),
                local=Sum("goods_services__contract_value_local"),
            )
            .exclude(usd__isnull=True)
            .order_by("-count")[:10]
        )
        by_number = []
        by_value = []
        by_buyer = []

        for_buyer = (
            Tender.objects.filter(**filter_args)
            .values("supplier__id", "supplier__supplier_name", "country__currency")
            .annotate(count=Count("buyer__id", distinct=True))
            .order_by("-count")[:10]
        )

        for value in for_value:
            a = {}
            a["amount_local"] = value["local"] if value["local"] else 0
            a["amount_usd"] = value["usd"] if value["usd"] else 0
            a["local_currency_code"] = value["country__currency"]
            a["supplier_id"] = value["supplier__id"]
            a["supplier_name"] = value["supplier__supplier_name"]
            a["tender_count"] = value["count"]
            by_value.append(a)
        for value in for_number:
            a = {}
            a["amount_local"] = value["local"] if value["local"] else 0
            a["amount_usd"] = value["usd"] if value["usd"] else 0
            a["local_currency_code"] = value["country__currency"]
            a["supplier_id"] = value["supplier__id"]
            a["supplier_name"] = value["supplier__supplier_name"]
            a["tender_count"] = value["count"]
            by_number.append(a)

        for value in for_buyer:
            a = {}
            a["supplier_id"] = value["supplier__id"]
            a["local_currency_code"] = value["country__currency"]
            a["supplier_name"] = value["supplier__supplier_name"]
            a["buyer_count"] = value["count"]
            by_buyer.append(a)

        return JsonResponse({"by_number": by_number, "by_value": by_value, "by_buyer": by_buyer})


class TopBuyers(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        country = self.request.GET.get("country", None)
        supplier = self.request.GET.get("supplier")

        filter_args = {}
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)
        filter_args["buyer__isnull"] = False
        filter_args["goods_services__contract_value_usd__isnull"] = False
        for_value = (
            Tender.objects.filter(**filter_args)
            .values("buyer__id", "buyer__buyer_name", "country__currency")
            .annotate(
                count=Count("id"),
                usd=Sum("goods_services__contract_value_usd"),
                local=Sum("goods_services__contract_value_local"),
            )
            .order_by("-usd")[:10]
        )
        for_number = (
            Tender.objects.filter(**filter_args)
            .exclude(goods_services__contract_value_usd__isnull=True)
            .values("buyer__id", "buyer__buyer_name", "country__currency")
            .annotate(
                count=Count("goods_services__contract__id", distinct=True),
                usd=Sum("goods_services__contract_value_usd"),
                local=Sum("goods_services__contract_value_local"),
            )
            .order_by("-count")[:10]
        )
        by_number = []
        by_value = []
        for value in for_value:
            a = {}
            a["amount_local"] = value["local"] if value["usd"] else 0
            a["amount_usd"] = value["usd"] if value["usd"] else 0
            a["local_currency_code"] = value["country__currency"]
            a["buyer_id"] = value["buyer__id"]
            a["buyer_name"] = value["buyer__buyer_name"]
            a["tender_count"] = value["count"]
            by_value.append(a)
        for value in for_number:
            a = {}
            a["amount_local"] = value["local"] if value["usd"] else 0
            a["amount_usd"] = value["usd"] if value["usd"] else 0
            a["local_currency_code"] = value["country__currency"]
            a["buyer_id"] = value["buyer__id"]
            a["buyer_name"] = value["buyer__buyer_name"]
            a["tender_count"] = value["count"]
            by_number.append(a)
        return JsonResponse({"by_number": by_number, "by_value": by_value})


class DirectOpen(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        supplier = self.request.GET.get("supplier")
        filter_args = {}
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)

        if country:
            amount_direct = (
                Tender.objects.filter(country__country_code_alpha_2=country, procurement_procedure="direct")
                .values("country__currency")
                .annotate(
                    count=Count("id"),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )
            amount_open = (
                Tender.objects.filter(country__country_code_alpha_2=country, procurement_procedure="open")
                .values("country__currency")
                .annotate(
                    count=Count("id"),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )
        elif buyer or supplier:
            amount_direct = (
                Tender.objects.filter(**filter_args, procurement_procedure="direct")
                .values("procurement_procedure")
                .annotate(
                    count=Count("id"),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )
            amount_open = (
                Tender.objects.filter(**filter_args, procurement_procedure="open")
                .values("procurement_procedure")
                .annotate(
                    count=Count("id"),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )
        else:
            amount_direct = (
                Tender.objects.filter(procurement_procedure="direct")
                .values("procurement_procedure")
                .annotate(
                    count=Count("id"),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )
            amount_open = (
                Tender.objects.filter(procurement_procedure="open")
                .values("procurement_procedure")
                .annotate(
                    count=Count("id"),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
            )

        country_currency = []
        if country:
            country_obj = Country.objects.filter(name=country)
            if country_obj:
                country_currency = country_obj.currency
        if amount_direct:
            for i in amount_direct:
                result_direct = {
                    "amount_local": i["local"] if i["local"] else 0,
                    "amount_usd": i["usd"] if i["usd"] else 0,
                    "tender_count": i["count"],
                    "local_currency_code": i["country__currency"] if "country__currency" in i else [],
                    "procedure": "direct",
                }
        else:
            result_direct = {
                "amount_local": 0,
                "amount_usd": 0,
                "tender_count": 0,
                "local_currency_code": country_currency,
                "procedure": "direct",
            }

        if amount_open:
            for i in amount_open:
                result_open = {
                    "amount_local": i["local"] if i["local"] else 0,
                    "amount_usd": i["usd"] if i["usd"] else 0,
                    "tender_count": i["count"],
                    "local_currency_code": i["country__currency"] if "country__currency" in i else [],
                    "procedure": "open",
                }
        else:
            result_open = {
                "amount_local": 0,
                "amount_usd": 0,
                "tender_count": 0,
                "local_currency_code": country_currency,
                "procedure": "open",
            }

        result = [result_direct, result_open]

        return JsonResponse(result, safe=False)


class ContractStatusView(APIView):
    """
    Returns status wise grouped info about contracts
    """

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        result = list()
        currency_code = ""
        status = ["active", "completed", "cancelled", "not_identified"]
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")

        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)

        # Status code wise grouped sum of contract value
        contract_value_local_sum = (
            Tender.objects.filter(**filter_args)
            .values("status")
            .annotate(sum=Sum("goods_services__contract_value_local"))
        )
        contract_value_usd_sum = (
            Tender.objects.filter(**filter_args)
            .values("status")
            .annotate(sum=Sum("goods_services__contract_value_usd"))
        )

        # Status code wise grouped total number of contracts
        grouped_contract_no = Tender.objects.filter(**filter_args).values("status").annotate(count=Count("id"))

        if country:
            try:
                country_res = Country.objects.get(name=country)
                currency_code = country_res.currency
            except Exception as e:
                print(e)

        status_in_result = [i["status"] for i in contract_value_local_sum]
        for i in range(len(status)):
            if status[i] in status_in_result:
                result.append(
                    {
                        "amount_local": [
                            each["sum"] if each["sum"] else 0
                            for each in contract_value_local_sum
                            if status[i] == each["status"]
                        ][0],
                        "amount_usd": [
                            each["sum"] if each["sum"] else 0
                            for each in contract_value_usd_sum
                            if status[i] == each["status"]
                        ][0],
                        "tender_count": [
                            each["count"] if each["count"] else 0
                            for each in grouped_contract_no
                            if status[i] == each["status"]
                        ][0],
                        "local_currency_code": currency_code,
                        "status": status[i],
                    }
                )
            else:
                result.append(
                    {
                        "amount_local": 0,
                        "amount_usd": 0,
                        "tender_count": 0,
                        "local_currency_code": currency_code,
                        "status": status[i],
                    }
                )

        return JsonResponse(result, safe=False)


class QuantityCorrelation(APIView):
    today = datetime.datetime.now()

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        country = self.request.GET.get("country", None)
        filter_args = {}
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if country:
            contracts_quantity = (
                Tender.objects.filter(country__country_code_alpha_2=country)
                .annotate(month=TruncMonth("contract_date"))
                .values("month", "country__currency")
                .annotate(
                    count=Count("id"),
                    usd=Sum("goods_services__contract_value_usd"),
                    local=Sum("goods_services__contract_value_local"),
                )
                .order_by("-month")
            )
        else:
            contracts_quantity = (
                Tender.objects.annotate(month=TruncMonth("contract_date"))
                .values("month")
                .annotate(count=Count("id"), usd=Sum("goods_services__contract_value_usd"))
                .order_by("-month")
            )

        contracts_quantity_list = []

        for i in contracts_quantity:
            active_case = CovidMonthlyActiveCases.objects.filter(
                **filter_args, covid_data_date__year=i["month"].year, covid_data_date__month=i["month"].month
            ).values("active_cases_count", "death_count")
            active_case_count = 0
            death_count = 0
            try:
                for j in active_case:
                    if j["active_cases_count"] and j["death_count"]:
                        active_case_count += j["active_cases_count"]
                        death_count += j["death_count"]
            except Exception:
                active_case_count = 0
                death_count = 0
            a = {}
            a["active_cases"] = active_case_count
            a["death_cases"] = death_count
            a["amount_local"] = i["local"] if "local" in i else ""
            a["amount_usd"] = i["usd"]
            a["local_currency_code"] = i["country__currency"] if "country__currency" in i else ""
            a["month"] = i["month"]
            a["tender_count"] = i["count"]
            contracts_quantity_list.append(a)

        return JsonResponse(contracts_quantity_list, safe=False)


class MonopolizationView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)

        # Month wise average of number of bids for contracts
        monthwise_data = (
            Tender.objects.filter(**filter_args)
            .annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(count_supplier=Count("supplier__supplier_id", distinct=True), count_contract=Count("id"))
            .order_by("-month")
        )
        final_line_chart_data = [
            {
                "date": monthwise_data[i]["month"],
                "value": round(monthwise_data[i]["count_contract"] / monthwise_data[i]["count_supplier"])
                if monthwise_data[i]["count_supplier"] and monthwise_data[i]["count_contract"]
                else 0,
            }
            for i in range(len(monthwise_data))
        ]

        # Difference percentage calculation

        # Overall average number of bids for contracts
        overall = Tender.objects.filter(**filter_args).aggregate(
            count_supplier=Count("supplier__supplier_id", distinct=True), count_contract=Count("id")
        )

        result = {
            "average": round(overall["count_contract"] / overall["count_supplier"])
            if overall["count_contract"] and overall["count_supplier"]
            else 0,
            "line_chart": final_line_chart_data,
        }
        return JsonResponse(result)


class CountrySuppliersView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        count = int(self.request.GET.get("count", 5))
        if country:
            filter_args["country__country_code_alpha_2"] = country

        usd_amountwise_sorted = (
            Tender.objects.filter(
                **filter_args, supplier__isnull=False, goods_services__goods_services_category__isnull=False
            )
            .values("supplier__id", "goods_services__goods_services_category__id")
            .annotate(usd=Sum("goods_services__contract_value_usd"))
            .exclude(usd__isnull=True)
            .order_by("-usd")
        )
        countwise_sorted = (
            Tender.objects.filter(
                **filter_args, supplier__isnull=False, goods_services__goods_services_category__isnull=False
            )
            .values("supplier__id", "goods_services__goods_services_category__id")
            .annotate(count=Count("id"))
            .exclude(count__isnull=True)
            .order_by("-count")
        )
        suppliers_dict = defaultdict(lambda: {"countwise": [], "amountwise": []})

        for i in usd_amountwise_sorted:
            if len(suppliers_dict[i["goods_services__goods_services_category__id"]]["amountwise"]) <= 5:
                suppliers_dict[i["goods_services__goods_services_category__id"]]["amountwise"].append(
                    i["supplier__id"]
                )
        for i in countwise_sorted:
            if len(suppliers_dict[i["goods_services__goods_services_category__id"]]["countwise"]) <= 5:
                suppliers_dict[i["goods_services__goods_services_category__id"]]["countwise"].append(i["supplier__id"])

        final_suppliers_list_countwise = list(
            itertools.chain.from_iterable([i["countwise"] for i in suppliers_dict.values()])
        )
        final_suppliers_list_amountwise = list(
            itertools.chain.from_iterable([i["amountwise"] for i in suppliers_dict.values()])
        )

        by_value_supplier_product = (
            Tender.objects.filter(
                **filter_args,
                supplier__id__in=final_suppliers_list_amountwise,
                supplier__isnull=False,
                goods_services__goods_services_category__isnull=False,
            )
            .values(
                "supplier__id",
                "supplier__supplier_name",
                "goods_services__goods_services_category__id",
                "goods_services__goods_services_category__category_name",
            )
            .annotate(
                local=Sum("goods_services__contract_value_local"),
                usd=Sum("goods_services__contract_value_usd"),
                count=Count("id"),
            )
            .order_by("-usd")[:count]
        )
        by_value_product_buyer = (
            Tender.objects.filter(
                **filter_args,
                supplier__id__in=final_suppliers_list_amountwise,
                buyer__isnull=False,
                goods_services__goods_services_category__isnull=False,
            )
            .values(
                "goods_services__goods_services_category__id",
                "goods_services__goods_services_category__category_name",
                "buyer__id",
                "buyer__buyer_name",
            )
            .annotate(
                local=Sum("goods_services__contract_value_local"),
                usd=Sum("goods_services__contract_value_usd"),
                count=Count("id"),
            )
            .order_by("-usd")[:count]
        )

        by_number_supplier_product = (
            Tender.objects.filter(
                **filter_args,
                supplier__id__in=final_suppliers_list_countwise,
                supplier__isnull=False,
                goods_services__goods_services_category__isnull=False,
            )
            .values(
                "supplier__id",
                "supplier__supplier_name",
                "goods_services__goods_services_category__id",
                "goods_services__goods_services_category__category_name",
            )
            .annotate(
                local=Sum("goods_services__contract_value_local"),
                usd=Sum("goods_services__contract_value_usd"),
                count=Count("id"),
            )
            .order_by("-count")[:count]
        )
        by_number_product_buyer = (
            Tender.objects.filter(
                **filter_args,
                supplier__id__in=final_suppliers_list_countwise,
                buyer__isnull=False,
                goods_services__goods_services_category__isnull=False,
            )
            .values(
                "goods_services__goods_services_category__id",
                "goods_services__goods_services_category__category_name",
                "buyer__id",
                "buyer__buyer_name",
            )
            .annotate(
                local=Sum("goods_services__contract_value_local"),
                usd=Sum("goods_services__contract_value_usd"),
                count=Count("id"),
            )
            .order_by("-count")[:count]
        )

        results = {
            "by_number": {
                "product_buyer": [
                    {
                        "amount_local": i["local"],
                        "amount_usd": i["usd"],
                        "buyer_id": i["buyer__id"],
                        "buyer_name": i["buyer__buyer_name"],
                        "product_id": i["goods_services__goods_services_category__id"],
                        "product_name": i["goods_services__goods_services_category__category_name"],
                        "tender_count": i["count"],
                    }
                    for i in by_number_product_buyer
                ],
                "supplier_product": [
                    {
                        "amount_local": i["local"],
                        "amount_usd": i["usd"],
                        "product_id": i["goods_services__goods_services_category__id"],
                        "product_name": i["goods_services__goods_services_category__category_name"],
                        "supplier_id": i["supplier__id"],
                        "supplier_name": i["supplier__supplier_name"],
                        "tender_count": i["count"],
                    }
                    for i in by_number_supplier_product
                ],
            },
            "by_value": {
                "product_buyer": [
                    {
                        "amount_local": i["local"],
                        "amount_usd": i["usd"],
                        "buyer_id": i["buyer__id"],
                        "buyer_name": i["buyer__buyer_name"],
                        "product_id": i["goods_services__goods_services_category__id"],
                        "product_name": i["goods_services__goods_services_category__category_name"],
                        "tender_count": i["count"],
                    }
                    for i in by_value_product_buyer
                ],
                "supplier_product": [
                    {
                        "amount_local": i["local"],
                        "amount_usd": i["usd"],
                        "product_id": i["goods_services__goods_services_category__id"],
                        "product_name": i["goods_services__goods_services_category__category_name"],
                        "supplier_id": i["supplier__id"],
                        "supplier_name": i["supplier__supplier_name"],
                        "tender_count": i["count"],
                    }
                    for i in by_value_supplier_product
                ],
            },
        }

        return JsonResponse(results)


class CountryMapView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        country = self.request.GET.get("country", None)
        try:
            country_instance = Country.objects.get(country_code_alpha_2=country)
        except Exception:
            return JsonResponse({"result": "Invalid Alpha Code"})
        if country is not None and country_instance is not None:
            tender_instance = Tender.objects.filter(country__country_code_alpha_2=country).aggregate(
                total_usd=Sum("goods_services__contract_value_usd"),
                total_local=Sum("goods_services__contract_value_local"),
            )
            count = Tender.objects.filter(country__country_code_alpha_2=country).count()
            final = {}
            final["country_code"] = country_instance.country_code_alpha_2
            final["country"] = country_instance.name
            final["country_continent"] = country_instance.continent
            final["amount_usd"] = tender_instance["total_usd"]
            final["amount_local"] = tender_instance["total_local"]
            final["tender_count"] = count
        else:
            final = {"result": "Invalid Alpha Code"}
        return JsonResponse(final)


class WorldMapView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        product = self.request.GET.get("product", None)
        filter_args = {}
        if product:
            filter_args["goods_services__goods_services_category__id"] = product
        country_instance = Country.objects.all().exclude(country_code_alpha_2="gl")
        result = []
        for country in country_instance:
            data = {}
            tender_instance = Tender.objects.filter(country=country, **filter_args).aggregate(
                total_usd=Sum("goods_services__contract_value_usd")
            )
            tender_count = Tender.objects.filter(country=country, **filter_args).count()
            data["country_code"] = country.country_code_alpha_2
            data["country"] = country.name
            data["country_continent"] = country.continent
            data["amount_usd"] = tender_instance["total_usd"]
            data["tender_count"] = tender_count
            result.append(data)
        return JsonResponse({"result": result})


class GlobalSuppliersView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        count = int(self.request.GET.get("count", 5))
        supplier = self.request.GET.get("supplier", None)
        product = self.request.GET.get("product", None)
        usd_amountwise_sorted = (
            Tender.objects.filter(supplier__isnull=False, goods_services__goods_services_category__isnull=False)
            .values("supplier__id", "goods_services__goods_services_category__id")
            .annotate(usd=Sum("goods_services__contract_value_usd"))
            .exclude(usd__isnull=True)
            .order_by("-usd")
        )
        countwise_sorted = (
            Tender.objects.filter(supplier__isnull=False, goods_services__goods_services_category__isnull=False)
            .values("supplier__id", "goods_services__goods_services_category__id")
            .annotate(count=Count("id"))
            .exclude(count__isnull=True)
            .order_by("-count")
        )
        suppliers_dict = defaultdict(lambda: {"countwise": [], "amountwise": []})

        for i in usd_amountwise_sorted:
            if len(suppliers_dict[i["goods_services__goods_services_category__id"]]["amountwise"]) <= count:
                suppliers_dict[i["goods_services__goods_services_category__id"]]["amountwise"].append(
                    i["supplier__id"]
                )
        for i in countwise_sorted:
            if len(suppliers_dict[i["goods_services__goods_services_category__id"]]["countwise"]) <= count:
                suppliers_dict[i["goods_services__goods_services_category__id"]]["countwise"].append(i["supplier__id"])
        print(suppliers_dict)
        if supplier:
            final_suppliers_list_countwise = [supplier]
            final_suppliers_list_amountwise = [supplier]
        else:
            final_suppliers_list_countwise = list(
                itertools.chain.from_iterable([i["countwise"] for i in suppliers_dict.values()])
            )
            final_suppliers_list_amountwise = list(
                itertools.chain.from_iterable([i["amountwise"] for i in suppliers_dict.values()])
            )
        if product:
            by_value_supplier_product = (
                Tender.objects.filter(
                    goods_services__goods_services_category__id=product,
                    supplier__id__in=final_suppliers_list_amountwise,
                    supplier__isnull=False,
                    goods_services__goods_services_category__isnull=False,
                )
                .values(
                    "supplier__id",
                    "supplier__supplier_name",
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                )
                .annotate(
                    local=Sum("goods_services__contract_value_local"),
                    usd=Sum("goods_services__contract_value_usd"),
                    count=Count("id"),
                )
                .order_by("-usd")
            )
            by_value_product_country = (
                Tender.objects.filter(
                    goods_services__goods_services_category__id=product,
                    supplier__id__in=final_suppliers_list_amountwise,
                    supplier__isnull=False,
                    goods_services__goods_services_category__isnull=False,
                )
                .values(
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                    "country__id",
                    "country__name",
                )
                .annotate(
                    local=Sum("goods_services__contract_value_local"),
                    usd=Sum("goods_services__contract_value_usd"),
                    count=Count("id"),
                )
                .order_by("-usd")
            )
            by_number_supplier_product = (
                Tender.objects.filter(
                    goods_services__goods_services_category__id=product,
                    supplier__id__in=final_suppliers_list_countwise,
                    supplier__isnull=False,
                    goods_services__goods_services_category__isnull=False,
                )
                .values(
                    "supplier__id",
                    "supplier__supplier_name",
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                )
                .annotate(
                    local=Sum("goods_services__contract_value_local"),
                    usd=Sum("goods_services__contract_value_usd"),
                    count=Count("id"),
                )
                .order_by("-count")
            )
            by_number_product_country = (
                Tender.objects.filter(
                    goods_services__goods_services_category__id=product,
                    supplier__id__in=final_suppliers_list_countwise,
                    supplier__isnull=False,
                    goods_services__goods_services_category__isnull=False,
                )
                .values(
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                    "country__id",
                    "country__name",
                )
                .annotate(
                    local=Sum("goods_services__contract_value_local"),
                    usd=Sum("goods_services__contract_value_usd"),
                    count=Count("id"),
                )
                .order_by("-count")
            )
        else:
            by_value_supplier_product = (
                Tender.objects.filter(
                    supplier__id__in=final_suppliers_list_amountwise,
                    supplier__isnull=False,
                    goods_services__goods_services_category__isnull=False,
                )
                .values(
                    "supplier__id",
                    "supplier__supplier_name",
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                )
                .annotate(
                    local=Sum("goods_services__contract_value_local"),
                    usd=Sum("goods_services__contract_value_usd"),
                    count=Count("id"),
                )
                .order_by("-usd")
            )
            by_value_product_country = (
                Tender.objects.filter(
                    supplier__id__in=final_suppliers_list_amountwise,
                    supplier__isnull=False,
                    goods_services__goods_services_category__isnull=False,
                )
                .values(
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                    "country__id",
                    "country__name",
                )
                .annotate(
                    local=Sum("goods_services__contract_value_local"),
                    usd=Sum("goods_services__contract_value_usd"),
                    count=Count("id"),
                )
                .order_by("-usd")
            )

            by_number_supplier_product = (
                Tender.objects.filter(
                    supplier__id__in=final_suppliers_list_countwise,
                    supplier__isnull=False,
                    goods_services__goods_services_category__isnull=False,
                )
                .values(
                    "supplier__id",
                    "supplier__supplier_name",
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                )
                .annotate(
                    local=Sum("goods_services__contract_value_local"),
                    usd=Sum("goods_services__contract_value_usd"),
                    count=Count("id"),
                )
                .order_by("-count")
            )
            by_number_product_country = (
                Tender.objects.filter(
                    supplier__id__in=final_suppliers_list_countwise,
                    supplier__isnull=False,
                    goods_services__goods_services_category__isnull=False,
                )
                .values(
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                    "country__id",
                    "country__name",
                )
                .annotate(
                    local=Sum("goods_services__contract_value_local"),
                    usd=Sum("goods_services__contract_value_usd"),
                    count=Count("id"),
                )
                .order_by("-count")
            )
        results = {
            "by_number": {
                "product_country": [
                    {
                        "amount_local": i["local"],
                        "amount_usd": i["usd"],
                        "country_id": i["country__id"],
                        "country_name": i["country__name"],
                        "product_id": i["goods_services__goods_services_category__id"],
                        "product_name": i["goods_services__goods_services_category__category_name"],
                        "tender_count": i["count"],
                    }
                    for i in by_number_product_country
                ],
                "supplier_product": [
                    {
                        "amount_local": i["local"],
                        "amount_usd": i["usd"],
                        "product_id": i["goods_services__goods_services_category__id"],
                        "product_name": i["goods_services__goods_services_category__category_name"],
                        "supplier_id": i["supplier__id"],
                        "supplier_name": i["supplier__supplier_name"],
                        "tender_count": i["count"],
                    }
                    for i in by_number_supplier_product
                ],
            },
            "by_value": {
                "product_country": [
                    {
                        "amount_local": i["local"],
                        "amount_usd": i["usd"],
                        "country_id": i["country__id"],
                        "country_name": i["country__name"],
                        "product_id": i["goods_services__goods_services_category__id"],
                        "product_name": i["goods_services__goods_services_category__category_name"],
                        "tender_count": i["count"],
                    }
                    for i in by_value_product_country
                ],
                "supplier_product": [
                    {
                        "amount_local": i["local"],
                        "amount_usd": i["usd"],
                        "product_id": i["goods_services__goods_services_category__id"],
                        "product_name": i["goods_services__goods_services_category__category_name"],
                        "supplier_id": i["supplier__id"],
                        "supplier_name": i["supplier__supplier_name"],
                        "tender_count": i["count"],
                    }
                    for i in by_value_supplier_product
                ],
            },
        }
        return JsonResponse(results)


class ProductDistributionView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer", None)
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            if buyer != "notnull":
                filter_args["contract__buyer__buyer_id"] = buyer
            else:
                filter_args["contract__buyer__isnull"] = False
        result = []
        goods_services = (
            GoodsServices.objects.filter(**filter_args)
            .values("goods_services_category__category_name", "goods_services_category__id")
            .annotate(
                tender=Count("goods_services_category"),
                local=Sum("contract_value_local"),
                usd=Sum("contract_value_usd"),
            )
        )
        for goods in goods_services:
            data = {}
            data["product_name"] = goods["goods_services_category__category_name"]
            data["product_id"] = goods["goods_services_category__id"]
            if country:
                instance = Country.objects.get(country_code_alpha_2=country)
                data["local_currency_code"] = instance.currency
            else:
                data["local_currency_code"] = "USD"
            data["tender_count"] = goods["tender"]
            data["amount_local"] = goods["local"]
            data["amount_usd"] = goods["usd"]
            result.append(data)
        return JsonResponse(result, safe=False)


class EquityIndicatorView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        if country:
            try:
                country_instance = Country.objects.get(country_code_alpha_2=country)
                filter_args["country"] = country_instance
                tenders_assigned = (
                    Tender.objects.filter(**filter_args)
                    .exclude(equity_category=None)
                    .aggregate(
                        total_usd=Sum("goods_services__contract_value_usd"),
                        total_local=Sum("goods_services__contract_value_local"),
                    )
                )
                assigned_count = Tender.objects.filter(**filter_args).exclude(equity_category=None).count()
                filter_args["equity_category"] = None
                tenders_unassigned = Tender.objects.filter(**filter_args).aggregate(
                    total_usd=Sum("goods_services__contract_value_usd"),
                    total_local=Sum("goods_services__contract_value_local"),
                )
                unassigned_count = Tender.objects.filter(**filter_args).count()
                data = [
                    {
                        "amount_local": tenders_assigned["total_local"],
                        "amount_usd": tenders_assigned["total_usd"],
                        "tender_count": assigned_count,
                        "local_currency_code": country_instance.currency,
                        "type": "assigned",
                    },
                    {
                        "amount_local": tenders_unassigned["total_local"],
                        "amount_usd": tenders_unassigned["total_usd"],
                        "tender_count": unassigned_count,
                        "local_currency_code": country_instance.currency,
                        "type": "unassigned",
                    },
                ]
                return JsonResponse(data, safe=False)
            except Exception:
                return JsonResponse([{"error": "Invalid country_code"}], safe=False)
        else:
            tenders_assigned = (
                Tender.objects.filter(**filter_args)
                .exclude(equity_category=None)
                .aggregate(
                    total_usd=Sum("goods_services__contract_value_usd"),
                    total_local=Sum("goods_services__contract_value_local"),
                )
            )
            assigned_count = Tender.objects.filter(**filter_args).exclude(equity_category=None).count()
            filter_args["equity_category"] = None
            tenders_unassigned = Tender.objects.filter(**filter_args).aggregate(
                total_usd=Sum("goods_services__contract_value_usd"),
                total_local=Sum("goods_services__contract_value_local"),
            )
            unassigned_count = Tender.objects.filter(**filter_args).count()
            data = [
                {
                    "amount_local": tenders_assigned["total_local"],
                    "amount_usd": tenders_assigned["total_usd"],
                    "tender_count": assigned_count,
                    "local_currency_code": "USD",
                    "type": "assigned",
                },
                {
                    "amount_local": tenders_unassigned["total_local"],
                    "amount_usd": tenders_unassigned["total_usd"],
                    "tender_count": unassigned_count,
                    "local_currency_code": "USD",
                    "type": "unassigned",
                },
            ]
            return JsonResponse(data, safe=False)


class ProductTimelineView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        supplier = self.request.GET.get("supplier")
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)
        result = []
        if country:
            try:
                country_instance = Country.objects.get(country_code_alpha_2=country)
                currency = country_instance.currency
                filter_args["country"] = country_instance
                tenders_assigned = (
                    Tender.objects.filter(**filter_args)
                    .exclude(goods_services__goods_services_category=None)
                    .annotate(month=TruncMonth("contract_date"))
                    .values(
                        "month",
                        "goods_services__goods_services_category__category_name",
                        "goods_services__goods_services_category__id",
                    )
                    .annotate(
                        count=Count("id"),
                        local=Sum("goods_services__contract_value_local"),
                        usd=Sum("goods_services__contract_value_usd"),
                    )
                    .order_by("-month")
                )
                for tender in tenders_assigned:
                    data = {}
                    data["amount_local"] = tender["local"]
                    data["amount_usd"] = tender["usd"]
                    data["date"] = tender["month"]
                    data["local_currency_code"] = currency
                    data["product_id"] = tender["goods_services__goods_services_category__id"]
                    data["product_name"] = tender["goods_services__goods_services_category__category_name"]
                    data["tender_count"] = tender["count"]
                    result.append(data)
                return JsonResponse(result, safe=False)
            except Exception:
                return JsonResponse([{"error": "Invalid country_code"}], safe=False)
        else:
            tenders_assigned = (
                Tender.objects.filter(**filter_args)
                .exclude(goods_services__goods_services_category=None)
                .annotate(month=TruncMonth("contract_date"))
                .values(
                    "month",
                    "goods_services__goods_services_category__category_name",
                    "goods_services__goods_services_category__id",
                )
                .annotate(
                    count=Count("id"),
                    local=Sum("goods_services__contract_value_local"),
                    usd=Sum("goods_services__contract_value_usd"),
                )
                .order_by("-month")
            )
            try:
                for tender in tenders_assigned:
                    data = {}
                    data["amount_local"] = tender["local"]
                    data["amount_usd"] = tender["usd"]
                    data["date"] = tender["month"]
                    data["local_currency_code"] = "USD"
                    data["product_id"] = tender["goods_services__goods_services_category__id"]
                    data["product_name"] = tender["goods_services__goods_services_category__category_name"]
                    data["tender_count"] = tender["count"]
                    result.append(data)
                return JsonResponse(result, safe=False)
            except Exception:
                return JsonResponse([{"error": "Invalid country_code"}], safe=False)
            return JsonResponse(data, safe=False)


class ProductTimelineRaceView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        supplier = self.request.GET.get("supplier")
        currency = "USD"
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)
        if country:
            filter_args["country__country_code_alpha_2"] = country
            instance = Country.objects.get(country_code_alpha_2=country)
            currency = instance.currency
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        cum_dict = {}
        final_data = []
        categories = GoodsServicesCategory.objects.all()
        tenders = (
            Tender.objects.exclude(goods_services__goods_services_category=None)
            .annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        for tender in tenders:
            end_date = tender["month"] + dateutil.relativedelta.relativedelta(months=1)
            start_date = tender["month"]
            result = {}
            result["month"] = str(start_date.year) + "-" + str(start_date.month)
            result["details"] = []
            for category in categories:
                data = {}
                if country:
                    good_services = (
                        GoodsServices.objects.filter(
                            contract__country__country_code_alpha_2=country,
                            goods_services_category=category,
                            contract__contract_date__gte=start_date,
                            contract__contract_date__lte=end_date,
                        )
                        .values("goods_services_category__category_name", "goods_services_category__id")
                        .annotate(count=Count("id"), local=Sum("contract_value_local"), usd=Sum("contract_value_usd"))
                    )
                else:
                    good_services = (
                        GoodsServices.objects.filter(
                            goods_services_category=category,
                            contract__contract_date__gte=start_date,
                            contract__contract_date__lte=end_date,
                        )
                        .values("goods_services_category__category_name", "goods_services_category__id")
                        .annotate(count=Count("id"), local=Sum("contract_value_local"), usd=Sum("contract_value_usd"))
                    )
                tender_count = Tender.objects.filter(
                    contract_date__gte=start_date,
                    contract_date__lte=end_date,
                    goods_services__goods_services_category=category,
                ).count()
                data["product_name"] = category.category_name
                data["product_id"] = category.id
                local_value = [i["local"] for i in good_services]
                usd_value = [i["usd"] for i in good_services]
                if category.category_name in cum_dict.keys():
                    if "local" in cum_dict[category.category_name].keys():
                        cum_dict[category.category_name]["local"] = cum_dict[category.category_name]["local"] + (
                            local_value[0] if local_value else 0
                        )
                    if "usd" in cum_dict[category.category_name].keys():
                        cum_dict[category.category_name]["usd"] = cum_dict[category.category_name]["usd"] + (
                            usd_value[0] if usd_value else 0
                        )
                    if "count" in cum_dict[category.category_name].keys():
                        cum_dict[category.category_name]["count"] = (
                            cum_dict[category.category_name]["count"] + tender_count
                        )
                else:
                    cum_dict[category.category_name] = {"local": 0, "usd": 0, "count": 0}
                    print(local_value)
                    cum_dict[category.category_name]["local"] = cum_dict[category.category_name]["local"] + (
                        local_value[0] if local_value else 0
                    )
                    cum_dict[category.category_name]["usd"] = cum_dict[category.category_name]["usd"] + (
                        usd_value[0] if usd_value else 0
                    )
                    cum_dict[category.category_name]["count"] = (
                        cum_dict[category.category_name]["count"] + tender_count
                    )
                data["amount_local"] = cum_dict[category.category_name]["local"]
                data["amount_usd"] = cum_dict[category.category_name]["usd"]
                data["currency"] = currency
                data["tender_count"] = cum_dict[category.category_name]["count"]
                result["details"].append(data)
            final_data.append(result)
        return JsonResponse(final_data, safe=False)


class SupplierProfileView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        data = {}
        try:
            instance = Supplier.objects.get(id=pk)
            supplier_detail = (
                Tender.objects.filter(supplier_id=pk)
                .values("country__name", "country__country_code_alpha_2")
                .annotate(
                    total_usd=Sum("goods_services__contract_value_usd"),
                    total_local=Sum("goods_services__contract_value_local"),
                )
            )
            tender_count = Tender.objects.filter(supplier_id=pk).count()
            data["name"] = instance.supplier_name
            data["id"] = pk
            data["code"] = instance.supplier_id
            data["address"] = instance.supplier_address
            data["amount_usd"] = supplier_detail[0]["total_usd"]
            data["amount_local"] = supplier_detail[0]["total_local"]
            data["tender_count"] = tender_count
            data["country_code"] = supplier_detail[0]["country__country_code_alpha_2"]
            data["country_name"] = supplier_detail[0]["country__name"]
            return JsonResponse(data, safe=False)
        except Exception:
            data["error"] = "Enter valid ID"
            return JsonResponse(data, safe=False)


class BuyerProfileView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        data = {}
        try:
            instance = Buyer.objects.get(id=pk)
            buyer_detail = (
                Tender.objects.filter(buyer_id=pk)
                .values("country__name", "country__country_code_alpha_2")
                .annotate(
                    total_usd=Sum("goods_services__contract_value_usd"),
                    total_local=Sum("goods_services__contract_value_local"),
                )
            )
            tender_count = Tender.objects.filter(buyer_id=pk).count()
            data["name"] = instance.buyer_name
            data["id"] = pk
            data["code"] = instance.buyer_id
            data["address"] = instance.buyer_address
            data["amount_usd"] = buyer_detail[0]["total_usd"]
            data["amount_local"] = buyer_detail[0]["total_local"]
            data["tender_count"] = tender_count
            data["country_code"] = buyer_detail[0]["country__country_code_alpha_2"]
            data["country_name"] = buyer_detail[0]["country__name"]
            return JsonResponse(data, safe=False)
        except Exception:
            data["error"] = "Enter valid ID"
            return JsonResponse(data, safe=False)


class CountryPartnerView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        if country:
            filter_args["country__country_code_alpha_2"] = country
        try:
            data_provider = CountryPartner.objects.filter(**filter_args)
        except Exception:
            data_provider = [{"error": "Country partner doesnot exist for this country"}]
        result = []
        if data_provider:
            for i in data_provider:
                data = {}
                data["name"] = i.name
                data["description"] = i.description
                data["email"] = i.email
                data["website"] = i.website
                data["logo"] = str(i.logo)
                data["order"] = i.order
                data["country"] = str(i.country)
                result.append(data)
        else:
            result = {"error": "Country Partner not found for this country"}
        return JsonResponse(result, safe=False)


class DataProviderView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        if country:
            filter_args["country__country_code_alpha_2"] = country
        try:
            data_provider = DataProvider.objects.filter(**filter_args)
        except Exception:
            data_provider = [{"error": "Data Provider doesnot exist for this country"}]
        result = []
        if data_provider:
            for i in data_provider:
                data = {}
                data["name"] = i.name
                data["country"] = str(i.country)
                data["website"] = i.website
                data["logo"] = str(i.logo)
                data["remark"] = i.remark
                result.append(data)
        else:
            result = {"error": "Data Provider not found for this country"}
        return JsonResponse(result, safe=False)


class BuyerSummaryView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        result = {}
        trend = []
        current_time = datetime.datetime.now()
        previous_month_date = current_time - dateutil.relativedelta.relativedelta(months=-1)
        previous_month = previous_month_date.replace(day=1).date()
        if country:
            filter_args["country__country_code_alpha_2"] = country
        buyer_details = (
            Tender.objects.filter(**filter_args)
            .exclude(buyer__isnull=True)
            .annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(count=Count("buyer_id", distinct=True))
            .order_by("-month")
        )
        totals = (
            Tender.objects.filter(**filter_args)
            .exclude(buyer__isnull=True)
            .values("buyer")
            .distinct()
            .aggregate(total=Count("buyer"))
        )
        for details in buyer_details:
            data = {}
            data["buyer_count"] = details["count"]
            data["month"] = details["month"]
            trend.append(data)
        try:
            dates_in_details = [i["month"] for i in buyer_details]
            final_current_month_count = [
                buyer_details[0]["count"] if current_time.replace(day=1).date() in dates_in_details else 0
            ]
            final_previous_month_count = [buyer_details[1]["count"] if previous_month in dates_in_details else 0]
            percentage = round(
                ((final_current_month_count[0] - final_previous_month_count[0]) / final_previous_month_count[0]) * 100
            )
            print(final_current_month_count)
            print(final_previous_month_count)
        except Exception:
            percentage = 0
        result["total"] = totals["total"]
        result["percentage"] = percentage
        result["trend"] = trend
        return JsonResponse(result, safe=False)


class SupplierSummaryView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        result = {}
        trend = []
        current_time = datetime.datetime.now()
        previous_month_date = current_time - dateutil.relativedelta.relativedelta(months=-1)
        previous_month = previous_month_date.replace(day=1).date()
        if country:
            filter_args["country__country_code_alpha_2"] = country
        supplier_details = (
            Tender.objects.filter(**filter_args)
            .exclude(supplier__isnull=True)
            .annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(count=Count("supplier_id", distinct=True))
            .order_by("-month")
        )
        totals = (
            Tender.objects.filter(**filter_args)
            .exclude(supplier__isnull=True)
            .values("supplier")
            .distinct()
            .aggregate(total=Count("supplier"))
        )
        for details in supplier_details:
            data = {}
            data["supplier_count"] = details["count"]
            data["month"] = details["month"]
            trend.append(data)
        try:
            dates_in_details = [i["month"] for i in supplier_details]
            final_current_month_count = [
                supplier_details[0]["count"] if current_time.replace(day=1).date() in dates_in_details else 0
            ]
            final_previous_month_count = [supplier_details[1]["count"] if previous_month in dates_in_details else 0]
            percentage = round(
                ((final_current_month_count[0] - final_previous_month_count[0]) / final_previous_month_count[0]) * 100
            )
        except Exception:
            percentage = 0
        result["total"] = totals["total"]
        result["percentage"] = percentage
        result["trend"] = trend
        return JsonResponse(result, safe=False)


class ProductSummaryView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        currency = "USD"
        if country:
            filter_args["country__country_code_alpha_2"] = country
            instance = Country.objects.get(country_code_alpha_2=country)
            currency = instance.currency
        result = []
        tenders_assigned = (
            Tender.objects.filter(**filter_args)
            .exclude(goods_services__goods_services_category=None)
            .annotate(category=Count("goods_services__goods_services_category__category_name"))
            .values(
                "goods_services__goods_services_category__category_name", "goods_services__goods_services_category__id"
            )
            .annotate(
                count=Count("id"),
                local=Sum("goods_services__contract_value_local"),
                usd=Sum("goods_services__contract_value_usd"),
            )
        )
        for tender in tenders_assigned:
            data = {}
            data["amount_local"] = tender["local"]
            data["amount_usd"] = tender["usd"]
            data["local_currency_code"] = currency
            data["product_id"] = tender["goods_services__goods_services_category__id"]
            data["product_name"] = tender["goods_services__goods_services_category__category_name"]
            data["tender_count"] = tender["count"]
            result.append(data)
        return JsonResponse(result, safe=False)


class FilterParams(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, *args, **kwargs):
        try:
            buyers = Buyer.objects.values("id", "buyer_name")
            suppliers = Supplier.objects.values("id", "supplier_name")
            countries = Country.objects.values("id", "country_code", "name")
            products = GoodsServicesCategory.objects.values("id", "category_name")

            result_buyer = []
            result_supplier = []
            result_country = []
            result_product = []
            result = {}

            if buyers:
                result_buyer = [{"id": buyer["id"], "name": buyer["buyer_name"]} for buyer in buyers]
            if suppliers:
                result_supplier = [{"id": supplier["id"], "name": supplier["supplier_name"]} for supplier in suppliers]

            if countries:
                result_country = [
                    {"id": country["id"], "code": country["country_code"], "name": country["name"]}
                    for country in countries
                ]

            if products:
                result_product = [{"id": product["id"], "name": product["category_name"]} for product in products]

            result = {
                "buyer": result_buyer,
                "contracts": {
                    "method": [
                        {"label": "Direct", "value": "direct"},
                        {"label": "Limited", "value": "limited"},
                        {"label": "Open", "value": "open"},
                        {"label": "Other", "value": "other"},
                        {"label": "Selective", "value": "selective"},
                    ],
                    "status": [
                        {"label": "Active", "value": "active"},
                        {"label": "Cancelled", "value": "cancelled"},
                        {"label": "Completed", "value": "completed"},
                        {"label": "Other", "value": "other"},
                    ],
                },
                "country": result_country,
                "product": result_product,
                "supplier": result_supplier,
            }

            return JsonResponse(result, safe=False)

        except Exception:
            return JsonResponse([{"error": "No buyer and supplier data available"}], safe=False)


class EquitySummaryView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        if country:
            filter_args["country__country_code_alpha_2"] = country
        filter_args["equity_category__isnull"] = False
        result = []
        equity_summary = (
            Tender.objects.filter(**filter_args)
            .annotate(month=TruncMonth("contract_date"))
            .values("month", "equity_category", "equity_category__category_name")
            .annotate(
                total=Count("id"),
                local=Sum("goods_services__contract_value_local"),
                usd=Sum("goods_services__contract_value_usd"),
            )
            .order_by("-month")
        )
        for detail in equity_summary:
            data = {}
            data["amount_local"] = detail["local"]
            data["amount_usd"] = detail["usd"]
            data["equity"] = detail["equity_category__category_name"]
            data["equity_category_id"] = detail["equity_category"]
            data["month"] = detail["month"]
            data["tender_count"] = detail["total"]
            result.append(data)
        return JsonResponse(result, safe=False)


class ProductTableView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        if country:
            filter_args["country__country_code_alpha_2"] = country
        filter_args["goods_services__goods_services_category__isnull"] = False
        result = []
        product_tables = (
            Tender.objects.filter(**filter_args)
            .values(
                "goods_services__goods_services_category__category_name", "goods_services__goods_services_category__id"
            )
            .annotate(
                total=Count("id", distinct=True),
                local=Sum("goods_services__contract_value_local"),
                usd=Sum("goods_services__contract_value_usd"),
                buyer=Count("buyer", distinct=True),
                supplier=Count("supplier", distinct=True),
            )
        )
        for product in product_tables:
            data = {}
            data["amount_local"] = product["local"]
            data["amount_usd"] = product["usd"]
            data["product_id"] = product["goods_services__goods_services_category__id"]
            data["product_name"] = product["goods_services__goods_services_category__category_name"]
            data["buyer_count"] = product["buyer"]
            data["supplier_count"] = product["supplier"]
            data["tender_count"] = product["total"]
            result.append(data)
        return JsonResponse(result, safe=False)


class FilterParametersSuppliers(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        result = []
        country = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer", None)
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        try:
            if country:
                filter_args["country__country_code_alpha_2"] = country
                instance = Country.objects.get(country_code_alpha_2=country)
                country_code = instance.country_code_alpha_2
            filter_args["supplier__isnull"] = False
            suppliers = (
                Tender.objects.filter(**filter_args).values("supplier__id", "supplier__supplier_name").distinct()
            )
            for supplier in suppliers:
                data = {}
                data["id"] = supplier["supplier__id"]
                data["name"] = supplier["supplier__supplier_name"]
                if country:
                    data["country_code"] = country_code
                else:
                    data["country_code"] = "USD"
                result.append(data)
            return JsonResponse(result, safe=False)
        except Exception:
            return JsonResponse([{"error": "Country code doest not exists"}], safe=False)


class FilterParametersBuyers(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        result = []
        country = self.request.GET.get("country", None)
        supplier = self.request.GET.get("supplier", None)
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)
        try:
            if country:
                filter_args["country__country_code_alpha_2"] = country
                instance = Country.objects.get(country_code_alpha_2=country)
                country_code = instance.country_code_alpha_2
            filter_args["buyer__isnull"] = False
            buyers = Tender.objects.filter(**filter_args).values("buyer__id", "buyer__buyer_name").distinct()
            for buyer in buyers:
                data = {}
                data["id"] = buyer["buyer__id"]
                data["name"] = buyer["buyer__buyer_name"]
                if country:
                    data["country_code"] = country_code
                else:
                    data["country_code"] = "USD"
                result.append(data)
            return JsonResponse(result, safe=False)
        except Exception:
            return JsonResponse([{"error": "Country code doest not exists"}], safe=False)


class FilterParametersStatic(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        countries = Country.objects.values("id", "country_code", "name")
        products = GoodsServicesCategory.objects.values("id", "category_name")
        equities = EquityCategory.objects.values("id", "category_name")
        red_flags = RedFlag.objects.filter(implemented=True).values("id", "title")
        result_country = []
        result_product = []
        result_equity = []
        result_red_flag = []
        result = {}
        if countries:
            result_country = [
                {"id": country["id"], "code": country["country_code"], "name": country["name"]}
                for country in countries
            ]

        if products:
            result_product = [{"id": product["id"], "name": product["category_name"]} for product in products]

        if equities:
            result_equity = [{"id": equity["id"], "name": equity["category_name"]} for equity in equities]
        if red_flags:
            result_red_flag = [{"id": red_flag["id"], "name": red_flag["title"]} for red_flag in red_flags]
        result["method"] = [
            {"label": "Direct", "value": "direct"},
            {"label": "Limited", "value": "limited"},
            {"label": "Open", "value": "open"},
            {"label": "Other", "value": "other"},
            {"label": "Selective", "value": "selective"},
            {"label": "Not Identified", "value": "not_identified"},
        ]
        result["status"] = [
            {"label": "Active", "value": "active"},
            {"label": "Cancelled", "value": "cancelled"},
            {"label": "Completed", "value": "completed"},
            {"label": "Other", "value": "other"},
            {"label": "Not Identified", "value": "not_identified"},
        ]
        result["country"] = result_country
        result["products"] = result_product
        result["equity"] = result_equity
        result["red_flag"] = result_red_flag
        return JsonResponse(result, safe=False)


class ProductSpendingComparision(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        product = self.request.GET.get("product", None)
        if product:
            filter_args["goods_services__goods_services_category__id"] = product
            amount_usd_local = (
                Tender.objects.filter(**filter_args)
                .annotate(month=TruncMonth("contract_date"))
                .values(
                    "country__country_code",
                    "country__currency",
                    "month",
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                )
                .annotate(
                    usd=Sum("goods_services__contract_value_usd"), local=Sum("goods_services__contract_value_usd")
                )
                .order_by("-month")
            )
            count = (
                Tender.objects.filter(**filter_args)
                .annotate(month=TruncMonth("contract_date"))
                .values(
                    "country__country_code",
                    "country__currency",
                    "month",
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                )
                .annotate(count=Count("id"))
                .order_by("-month")
            )
            result = [
                {
                    "amount_local": i["local"],
                    "amount_usd": i["usd"],
                    "country_code": i["country__country_code"],
                    "currency": i["country__currency"],
                    "month": i["month"].strftime("%Y-%m"),
                    "product_id": i["goods_services__goods_services_category__id"],
                    "product_name": i["goods_services__goods_services_category__category_name"],
                }
                for i in amount_usd_local
            ]
            for i in range(len(count)):
                result[i]["tender_count"] = count[i]["count"]
            return JsonResponse(result, safe=False)
        else:
            amount_usd_local = (
                Tender.objects.annotate(month=TruncMonth("contract_date"))
                .values(
                    "country__country_code",
                    "country__currency",
                    "month",
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                )
                .annotate(
                    usd=Sum("goods_services__contract_value_usd"), local=Sum("goods_services__contract_value_usd")
                )
                .order_by("-month")
            )
            count = (
                Tender.objects.annotate(month=TruncMonth("contract_date"))
                .values(
                    "country__country_code",
                    "country__currency",
                    "month",
                    "goods_services__goods_services_category__id",
                    "goods_services__goods_services_category__category_name",
                )
                .annotate(count=Count("id"))
                .order_by("-month")
            )
            result = [
                {
                    "amount_local": i["local"],
                    "amount_usd": i["usd"],
                    "country_code": i["country__country_code"],
                    "currency": i["country__currency"],
                    "month": i["month"].strftime("%Y-%m"),
                    "product_id": i["goods_services__goods_services_category__id"],
                    "product_name": i["goods_services__goods_services_category__category_name"],
                }
                for i in amount_usd_local
            ]
            for i in range(len(count)):
                result[i]["tender_count"] = count[i]["count"]
            return JsonResponse(result, safe=False)


class SlugBlogShow(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, *args, **kwargs):
        content_type = self.kwargs["type"]
        slug = self.kwargs["slug"]
        result = {}
        try:
            if content_type:
                results = InsightsPage.objects.filter(contents_type=content_type.title(), slug=slug).values(
                    "title", "published_date", "body", "author", "country_id", "featured", "content_image_id"
                )
                result["title"] = results[0]["title"]
                result["published_date"] = results[0]["published_date"]
                result["body"] = results[0]["body"]
                result["author"] = results[0]["author"]
                result["featured"] = results[0]["featured"]
                result["country_id"] = results[0]["country_id"]
                result["content_image_id"] = results[0]["content_image_id"]

        except Exception:
            result = [{"error": "Content doest not exists"}]
        return JsonResponse(result, safe=False)


class SlugStaticPageShow(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, *args, **kwargs):
        page_type = self.kwargs["type"]
        result = {}
        try:
            if page_type:
                results = StaticPage.objects.filter(page_type=page_type.title()).values("page_type", "body")
                result["page_type"] = results[0]["page_type"]
                result["body"] = results[0]["body"]

        except Exception:
            result = [{"error": "Content doest not exists"}]

        return JsonResponse(result, safe=False)


class BuyerTrendView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        temp = {}
        tender_temp = {}
        data = []
        count = (
            Tender.objects.annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(
                total_buyer_count=Count("buyer__id", distinct=True), sum=Sum("goods_services__contract_value_usd")
            )
            .order_by("month")
        )
        countries = Country.objects.all()
        for i in count:
            result = {}
            end_date = i["month"] + dateutil.relativedelta.relativedelta(months=1)
            start_date = i["month"]
            result["details"] = []
            result["month"] = str(start_date.year) + "-" + str(start_date.month)
            for j in countries:
                b = {}
                tender = Tender.objects.filter(
                    country__country_code_alpha_2=j.country_code_alpha_2,
                    contract_date__gte=start_date,
                    contract_date__lte=end_date,
                ).aggregate(
                    total_buyer_count=Count("buyer__id", distinct=True),
                    amount_usd=Sum("goods_services__contract_value_usd"),
                )
                b["country"] = j.name
                b["country_code"] = j.country_code_alpha_2
                b["country_continent"] = j.continent
                buyer_count = tender["total_buyer_count"]
                if tender["amount_usd"] is None:
                    tender_val = 0
                else:
                    tender_val = tender["amount_usd"]
                if buyer_count is None:
                    buyer_val = 0
                else:
                    buyer_val = buyer_count
                if bool(temp) and j.name in temp.keys():
                    current_val = temp[j.name]
                    cum_value = current_val + tender_val
                    temp[j.name] = cum_value
                    b["amount_usd"] = cum_value
                else:
                    temp[j.name] = tender_val
                    b["amount_usd"] = tender_val
                if bool(tender_temp) and j.name in tender_temp.keys():
                    current_val = tender_temp[j.name]
                    cum_value = current_val + buyer_val
                    tender_temp[j.name] = cum_value
                    b["buyer_count"] = cum_value
                else:
                    tender_temp[j.name] = buyer_val
                    b["buyer_count"] = buyer_val
                result["details"].append(b)
            data.append(result)
        return JsonResponse({"result": data})


class SupplierTrendView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        temp = {}
        tender_temp = {}
        data = []
        count = (
            Tender.objects.annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(
                total_buyer_count=Count("supplier__id", distinct=True), sum=Sum("goods_services__contract_value_usd")
            )
            .order_by("month")
        )
        countries = Country.objects.all()
        for i in count:
            result = {}
            end_date = i["month"] + dateutil.relativedelta.relativedelta(months=1)
            start_date = i["month"]
            result["details"] = []
            result["month"] = str(start_date.year) + "-" + str(start_date.month)
            for j in countries:
                b = {}
                tender = Tender.objects.filter(
                    country__country_code_alpha_2=j.country_code_alpha_2,
                    contract_date__gte=start_date,
                    contract_date__lte=end_date,
                ).aggregate(
                    total_supplier_count=Count("supplier__id", distinct=True),
                    amount_usd=Sum("goods_services__contract_value_usd"),
                )
                b["country"] = j.name
                b["country_code"] = j.country_code_alpha_2
                b["country_continent"] = j.continent
                supplier_count = tender["total_supplier_count"]
                if tender["amount_usd"] is None:
                    tender_val = 0
                else:
                    tender_val = tender["amount_usd"]
                if supplier_count is None:
                    supplier_val = 0
                else:
                    supplier_val = supplier_count
                if bool(temp) and j.name in temp.keys():
                    current_val = temp[j.name]
                    cum_value = current_val + tender_val
                    temp[j.name] = cum_value
                    b["amount_usd"] = cum_value
                else:
                    temp[j.name] = tender_val
                    b["amount_usd"] = tender_val
                if bool(tender_temp) and j.name in tender_temp.keys():
                    current_val = tender_temp[j.name]
                    cum_value = current_val + supplier_val
                    tender_temp[j.name] = cum_value
                    b["supplier_count"] = cum_value
                else:
                    tender_temp[j.name] = supplier_val
                    b["supplier_count"] = supplier_val
                result["details"].append(b)
            data.append(result)
        return JsonResponse({"result": data})


class DirectOpenContractTrendView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        temp = {}
        tender_temp = {}
        data = []
        count = (
            Tender.objects.annotate(month=TruncMonth("contract_date"))
            .values("month")
            .annotate(total_contract=Count("id"), total_amount=Sum("goods_services__contract_value_usd"))
            .order_by("month")
        )
        countries = Country.objects.all().exclude(country_code_alpha_2="gl")
        for i in count:
            result = {}
            end_date = i["month"] + dateutil.relativedelta.relativedelta(months=1)
            start_date = i["month"]
            result["details"] = []
            result["month"] = str(start_date.year) + "-" + str(start_date.month)
            for j in countries:
                b = {}
                contracts = ["direct", "Direct", "open", "Open"]
                tender_count = Tender.objects.filter(
                    country__country_code_alpha_2=j.country_code_alpha_2,
                    contract_date__gte=start_date,
                    contract_date__lte=end_date,
                    procurement_procedure__in=contracts,
                ).count()
                tender = Tender.objects.filter(
                    country__country_code_alpha_2=j.country_code_alpha_2,
                    contract_date__gte=start_date,
                    contract_date__lte=end_date,
                    procurement_procedure__in=contracts,
                ).aggregate(Sum("goods_services__contract_value_usd"))
                b["country"] = j.name
                b["country_code"] = j.country_code_alpha_2
                b["country_continent"] = j.continent
                if tender["goods_services__contract_value_usd__sum"] is None:
                    tender_val = 0
                else:
                    tender_val = tender["goods_services__contract_value_usd__sum"]
                if tender_count is None:
                    contract_val = 0
                else:
                    contract_val = tender_count
                if bool(temp) and j.name in temp.keys():
                    current_val = temp[j.name]
                    cum_value = current_val + tender_val
                    temp[j.name] = cum_value
                    b["amount_usd"] = cum_value
                else:
                    temp[j.name] = tender_val
                    b["amount_usd"] = tender_val
                if bool(tender_temp) and j.name in tender_temp.keys():
                    current_val = tender_temp[j.name]
                    cum_value = current_val + contract_val
                    tender_temp[j.name] = cum_value
                    b["tender_count"] = cum_value
                else:
                    tender_temp[j.name] = contract_val
                    b["tender_count"] = contract_val
                result["details"].append(b)
            data.append(result)
        return JsonResponse({"result": data})


class ContractRedFlagsView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        supplier = self.request.GET.get("supplier", None)
        buyer = self.request.GET.get("buyer", None)
        product = self.request.GET.get("product", None)
        if country:
            filter_args["country__country_code_alpha_2"] = country
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)
        if buyer:
            filter_args = add_filter_args("buyer", buyer, filter_args)
        if product:
            filter_args["goods_services__goods_services_category__id"] = product
        red_flags = RedFlag.objects.filter(implemented=True)
        value = []
        result = {"result": value}
        for red_flag in red_flags:
            count = Tender.objects.filter(**filter_args, red_flag__pk=red_flag.id).distinct().count()
            data = {}
            data["red_flag_id"] = red_flag.id
            data["red_flag"] = red_flag.title
            data["tender_count"] = count
            value.append(data)
        return JsonResponse(result, safe=False)


class RedFlagSummaryView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filter_args = {}
        country = self.request.GET.get("country", None)
        if country:
            filter_args["country__country_code_alpha_2"] = country
        filter_args["red_flag__isnull"] = False
        result = []
        equity_summary = (
            Tender.objects.filter(**filter_args)
            .annotate(month=TruncMonth("contract_date"))
            .values("month", "red_flag", "red_flag__title", "red_flag__implemented")
            .annotate(
                total=Count("id"),
                local=Sum("goods_services__contract_value_local"),
                usd=Sum("goods_services__contract_value_usd"),
            )
            .order_by("-month")
        )
        for detail in equity_summary:
            if detail["red_flag__implemented"]:
                data = {}
                data["amount_local"] = detail["local"]
                data["amount_usd"] = detail["usd"]
                data["red_flag"] = detail["red_flag__title"]
                data["red_flag_id"] = detail["red_flag"]
                data["month"] = detail["month"]
                data["tender_count"] = detail["total"]
                result.append(data)
        return JsonResponse(result, safe=False)


class UpcomingEventView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        result = {}
        today = datetime.datetime.now()
        results = EventsPage.objects.filter(event_date__gte=today).values(
            "title", "description", "event_date", "time_from", "time_to", "location", "event_image_id"
        )
        result["title"] = results[0]["title"]
        result["description"] = results[0]["description"]
        result["event_date"] = results[0]["event_date"]
        result["time_from"] = results[0]["time_from"]
        result["time_to"] = results[0]["time_to"]
        result["location"] = results[0]["location"]

        return JsonResponse(result, safe=False)
