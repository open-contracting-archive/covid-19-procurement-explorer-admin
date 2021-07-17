from celery import Celery

from country.models import GoodsServices
from country.tasks import convert_local_to_usd

app = Celery()


@app.task(name="process_currency_conversion")
def process_currency_conversion(
    tender_value_local, award_value_local, contract_value_local, tender_date, currency, id
):
    tender_value_usd = (
        convert_local_to_usd(source_value=tender_value_local, conversion_date=tender_date, source_currency=currency)
        if tender_value_local
        else None
    )
    award_value_usd = (
        convert_local_to_usd(source_value=award_value_local, conversion_date=tender_date, source_currency=currency)
        if award_value_local
        else None
    )
    contract_value_usd = (
        convert_local_to_usd(source_value=contract_value_local, conversion_date=tender_date, source_currency=currency)
        if contract_value_local
        else None
    )
    print(f"started processing... {id}: {tender_value_usd}, {award_value_usd}, {contract_value_usd}")
    if tender_value_usd or award_value_usd or contract_value_usd:
        tender = GoodsServices.objects.get(id=id)
        tender.tender_value_usd = tender_value_usd
        tender.award_value_usd = award_value_usd
        tender.contract_value_usd = contract_value_usd
        tender.save()
        print("Converted goodsservices id:" + str(tender.id))
    print(f"end of {id}")
