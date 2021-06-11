from django.db.models import Count, F, Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Supplier, Tender
from visualization.helpers.general import page_expire_period


class ProductFlowView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request, *args, **kwargs):
        product_id = self.kwargs["pk"]
        temp_country_list = []
        by_value_product_country = []
        temp_tender_country_list = []
        by_number_product_country = []
        usd_amountwise_sorted = (
            Tender.objects.filter(
                goods_services__goods_services_category__id=product_id,
                supplier__isnull=False,
                goods_services__goods_services_category__isnull=False,
            )
            .values(
                "supplier__id",
                "goods_services__goods_services_category__id",
                "country__id",
                "country__name",
                "goods_services__goods_services_category__category_name",
            )
            .exclude(contract_value_usd__isnull=True)
            .annotate(
                count=Count("id"),
                product_name=F("goods_services__goods_services_category__category_name"),
                product_id=F("goods_services__goods_services_category__id"),
                contract_value_usd=F("contract_value_usd"),
                contract_value_local=F("contract_value_local"),
            )
            .order_by("-contract_value_usd")
        )
        tender_countwise_sorted = (
            Tender.objects.filter(
                goods_services__goods_services_category__id=product_id,
                supplier__isnull=False,
                goods_services__goods_services_category__isnull=False,
            )
            .values(
                "supplier__id",
                "goods_services__goods_services_category__id",
                "country__id",
                "country__name",
                "goods_services__goods_services_category__category_name",
            )
            .annotate(
                count=Count("id"),
                product_name=F("goods_services__goods_services_category__category_name"),
                product_id=F("goods_services__goods_services_category__id"),
                contract_value_usd=F("contract_value_usd"),
                contract_value_local=F("contract_value_local"),
            )
            .exclude(count__isnull=True)
            .order_by("-count")
        )
        for i in usd_amountwise_sorted:
            if i["country__id"] not in temp_country_list:
                temp_country_list.append(i["country__id"])
                by_value_product_country.append(i)

        for i in tender_countwise_sorted:
            if i["country__id"] not in temp_tender_country_list:
                temp_tender_country_list.append(i["country__id"])
                by_number_product_country.append(i)

        by_number_supplier_product = (
            Supplier.objects.filter(
                tenders__goods_services__goods_services_category__id=product_id,
                tenders__goods_services__goods_services_category__isnull=False,
            )
            .values(
                "tenders__supplier__id",
                "tenders__goods_services__goods_services_category__id",
                "tenders__goods_services__goods_services_category__category_name",
                "tenders__supplier__supplier_name",
            )
            .annotate(
                count=Count("tenders__id"),
                contract_value_usd=Sum("tenders__contract_value_usd"),
                contract_value_local=Sum("tenders__contract_value_local"),
            )
            .order_by("-count")
        )
        by_value_supplier_product = (
            Supplier.objects.filter(
                tenders__goods_services__goods_services_category__id=product_id,
                tenders__goods_services__goods_services_category__isnull=False,
            )
            .values(
                "tenders__supplier__id",
                "tenders__goods_services__goods_services_category__id",
                "tenders__goods_services__goods_services_category__category_name",
                "tenders__supplier__supplier_name",
            )
            .annotate(
                count=Count("tenders__id"),
                contract_value_usd=Sum("tenders__contract_value_usd"),
                contract_value_local=Sum("tenders__contract_value_local"),
            )
            .order_by("-contract_value_usd")
        )
        results = {
            "by_number": {
                "product_country": [
                    {
                        "amount_local": i["contract_value_local"],
                        "amount_usd": i["contract_value_usd"],
                        "country_id": i["country__id"],
                        "country_name": i["country__name"],
                        "product_id": i["product_id"],
                        "product_name": i["product_name"],
                        "tender_count": i["count"],
                    }
                    for i in by_number_product_country
                ],
                "supplier_product": [
                    {
                        "amount_local": i["contract_value_local"],
                        "amount_usd": i["contract_value_usd"],
                        "product_id": i["tenders__goods_services__goods_services_category__id"],
                        "product_name": i["tenders__goods_services__goods_services_category__category_name"],
                        "supplier_id": i["tenders__supplier__id"],
                        "supplier_name": i["tenders__supplier__supplier_name"],
                        "tender_count": i["count"],
                    }
                    for i in by_number_supplier_product[:5]
                ],
            },
            "by_value": {
                "product_country": [
                    {
                        "amount_local": i["contract_value_local"],
                        "amount_usd": i["contract_value_usd"],
                        "country_id": i["country__id"],
                        "country_name": i["country__name"],
                        "product_id": i["product_id"],
                        "product_name": i["product_name"],
                        "tender_count": i["count"],
                    }
                    for i in by_value_product_country
                ],
                "supplier_product": [
                    {
                        "amount_local": i["contract_value_local"],
                        "amount_usd": i["contract_value_usd"],
                        "product_id": i["tenders__goods_services__goods_services_category__id"],
                        "product_name": i["tenders__goods_services__goods_services_category__category_name"],
                        "supplier_id": i["tenders__supplier__id"],
                        "supplier_name": i["tenders__supplier__supplier_name"],
                        "tender_count": i["count"],
                    }
                    for i in by_value_supplier_product[:5]
                ],
            },
        }
        return JsonResponse(results)
