import itertools
from collections import defaultdict

from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period


class CountrySuppliersView(APIView):
    @method_decorator(cache_page(page_expire_period()))
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
            .annotate(usd=Sum("contract_value_usd"))
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

        final_suppliers_list_amountwise = list(
            itertools.chain.from_iterable([i["amountwise"] for i in suppliers_dict.values()])
        )

        product_supplier = (
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
                local=Sum("contract_value_local"),
                usd=Sum("contract_value_usd"),
                count=Count("id"),
            )
        )

        product_buyer = (
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
                local=Sum("contract_value_local"),
                usd=Sum("contract_value_usd"),
                count=Count("id"),
            )
        )

        by_value_product_buyer = (product_buyer.order_by("-usd"))[:count]
        by_number_product_buyer = (product_buyer.order_by("-count"))[:count]

        by_value_product_supplier = (product_supplier.order_by("-usd"))[:count]
        by_number_product_supplier = (product_supplier.order_by("-count"))[:count]

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
                    for i in by_number_product_supplier
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
                    for i in by_value_product_supplier
                ],
            },
        }

        return JsonResponse(results)
