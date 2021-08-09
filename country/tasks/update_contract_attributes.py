from celery import Celery

from country.models import Tender

app = Celery()


@app.task(name="update_contract_attributes")
def update_contract_attributes(contract_ids):
    if type(contract_ids) is not list:
        contract_ids = [contract_ids]

    for contract_id in contract_ids:
        contract = Tender.objects.get(id=contract_id)
        goods_services = list(
            contract.goods_services.all().values(
                "contract_title",
                "contract_value_usd",
                "award_value_usd",
                "tender_value_usd",
                "contract_value_local",
                "award_value_local",
                "tender_value_local",
            )
        )
        contract_titles = [
            i.get("contract_title")
            for i in goods_services
            if i.get("contract_title") is not None
            if not i.get("contract_title")
        ]
        contract_titles.append(contract.contract_title)

        contract.contract_title = ", ".join(set(contract_titles))
        contract.contract_value_usd = sum(
            [i.get("contract_value_usd") for i in goods_services if i.get("contract_value_usd") != 0]
        )
        contract.contract_value_local = sum(
            [i.get("contract_value_local") for i in goods_services if i.get("contract_value_local") != 0]
        )
        contract.tender_value_local = sum(
            [i.get("tender_value_local") for i in goods_services if i.get("tender_value_local") != 0]
        )
        contract.tender_value_usd = sum(
            [i.get("tender_value_usd") for i in goods_services if i.get("tender_value_usd") != 0]
        )
        contract.award_value_local = sum(
            [i.get("award_value_local") for i in goods_services if i.get("award_value_local") != 0]
        )
        contract.award_value_usd = sum(
            [i.get("award_value_usd") for i in goods_services if i.get("award_value_usd") != 0]
        )
        contract.save()

    return True
