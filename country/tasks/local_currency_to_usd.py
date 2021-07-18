from celery import Celery

from country.models import GoodsServices
from country.tasks.convert_local_to_usd import convert_local_to_usd

app = Celery()


@app.task(name="local_currency_to_usd")
def local_currency_to_usd(goods_services_row_id, conversion_date, source_currency, source_values):
    dst_tender_value = convert_local_to_usd(
        conversion_date, source_currency, source_values["tender_value_local"], dst_currency="USD"
    )
    dst_award_value = convert_local_to_usd(
        conversion_date, source_currency, source_values["award_value_local"], dst_currency="USD"
    )
    dst_contract_value = convert_local_to_usd(
        conversion_date, source_currency, source_values["contract_value_local"], dst_currency="USD"
    )

    r = GoodsServices.objects.filter(id=goods_services_row_id).first()
    if r:
        r.tender_value_usd = dst_tender_value or None
        r.award_value_usd = dst_award_value or None
        r.contract_value_usd = dst_contract_value or None
        r.save()
