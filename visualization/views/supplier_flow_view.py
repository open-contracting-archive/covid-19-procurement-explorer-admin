from django.db.models import Count, F, Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from country.models import Supplier, Tender
from visualization.helpers.general import page_expire_period


class SupplierFlowView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request, *args, **kwargs):
        filter_args = {}
        supplier_id = self.kwargs["pk"]
        try:
            supplier_obj = Supplier.objects.get(id=supplier_id)
            product_ids = supplier_obj.goods_services.all().values("goods_services_category__id")
            product_list = [i["goods_services_category__id"] for i in product_ids]
            filter_args["goods_services__goods_services_category__id__in"] = product_list
        except Exception:
            filter_args = {}
        by_value_supplier_product = (
            Supplier.objects.filter(
                id=supplier_id,
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
        by_value_product_country = (
            Tender.objects.filter(
                **filter_args,
                supplier__id=supplier_id,
                supplier__isnull=False,
                goods_services__goods_services_category__isnull=False,
            )
            .values(
                "country__id",
                "country__name",
            )
            .annotate(
                count=Count("id"),
                contract_value_usd=Sum("contract_value_usd"),
                contract_value_local=Sum("contract_value_local"),
                product_name=F("goods_services__goods_services_category__category_name"),
                product_id=F("goods_services__goods_services_category__id"),
            )
            .order_by("-contract_value_usd")
        )
        by_number_supplier_product = (
            Supplier.objects.filter(
                id=supplier_id,
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
        by_number_product_country = (
            Tender.objects.filter(
                **filter_args,
                supplier__id=supplier_id,
                supplier__isnull=False,
                goods_services__goods_services_category__isnull=False,
            )
            .values(
                "country__id",
                "country__name",
            )
            .annotate(
                count=Count("id"),
                contract_value_usd=Sum("contract_value_usd"),
                contract_value_local=Sum("contract_value_local"),
                product_name=F("goods_services__goods_services_category__category_name"),
                product_id=F("goods_services__goods_services_category__id"),
            )
            .order_by("-count")
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
                    for i in by_number_supplier_product[:10]
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
                    for i in by_value_supplier_product[:10]
                ],
            },
        }
        return JsonResponse(results)
