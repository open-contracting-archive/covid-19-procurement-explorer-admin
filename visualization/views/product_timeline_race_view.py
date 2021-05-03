import dateutil.relativedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Country, GoodsServices, GoodsServicesCategory, Tender
from visualization.helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class ProductTimelineRaceView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        filter_args = {}
        country_code = self.request.GET.get("country", None)
        buyer = self.request.GET.get("buyer")
        supplier = self.request.GET.get("supplier")
        currency = "USD"
        if supplier:
            filter_args = add_filter_args("supplier", supplier, filter_args)
        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code
            instance = Country.objects.get(country_code_alpha_2=country_code)
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
            result = {"month": str(start_date.year) + "-" + str(start_date.month), "details": []}
            for category in categories:
                data = {}
                if country_code:
                    good_services = (
                        GoodsServices.objects.filter(
                            contract__country__country_code_alpha_2=country_code,
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
