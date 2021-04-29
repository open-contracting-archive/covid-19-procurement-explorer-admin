import itertools
from collections import defaultdict

from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Tender
from visualization.helpers.general import page_expire_period


class GlobalSuppliersView(APIView):
    @method_decorator(cache_page(page_expire_period()))
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
