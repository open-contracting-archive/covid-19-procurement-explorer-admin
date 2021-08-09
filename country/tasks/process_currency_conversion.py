from celery import Celery

from country.models import GoodsServices
from country.tasks.convert_local_to_usd import convert_local_to_usd

app = Celery()


@app.task(name="process_currency_conversion")
def process_currency_conversion(goods_services_id, conversion_date, source_currency):
    goods_services_object = GoodsServices.objects.filter(id=goods_services_id).first()

    if goods_services_object:
        if source_currency != "USD":
            goods_services_object.tender_value_usd = convert_local_to_usd(
                conversion_date, source_currency, goods_services_object.tender_value_local
            )
            goods_services_object.award_value_usd = convert_local_to_usd(
                conversion_date, source_currency, goods_services_object.award_value_local
            )
            goods_services_object.contract_value_usd = convert_local_to_usd(
                conversion_date, source_currency, goods_services_object.contract_value_local
            )
        else:
            goods_services_object.tender_value_usd = goods_services_object.tender_value_local
            goods_services_object.award_value_usd = goods_services_object.award_value_local
            goods_services_object.contract_value_usd = goods_services_object.contract_value_local

        goods_services_object.save()
