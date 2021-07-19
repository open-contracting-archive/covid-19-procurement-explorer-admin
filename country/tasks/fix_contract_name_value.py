from celery import Celery
from django.core import management

from country.models import Country, EquityCategory, EquityKeywords, Tender
from country.tasks.process_redflag import process_redflag
from country.tasks.process_redflag6 import process_redflag6
from country.tasks.process_redflag7 import process_redflag7
from visualization.helpers.scheduler import ScheduleRunner

app = Celery()


@app.task(name="fix_contract_name_value")
def fix_contract_name_value(tender_id, country):
    country_obj = Country.objects.filter(name=country).first()
    keywords = EquityKeywords.objects.filter(country=country_obj)
    if type(tender_id) is not list:
        tender_list = [tender_id]
    else:
        tender_list = tender_id
    for tender in tender_list:
        tender_instance = Tender.objects.get(id=tender)
        tender_instance.red_flag.clear()  # Clearing red-flag
        goods_services = list(
            tender_instance.goods_services.all().values(
                "contract_title",
                "contract_value_usd",
                "award_value_usd",
                "tender_value_usd",
                "contract_value_local",
                "award_value_local",
                "tender_value_local",
            )
        )
        contract_title = [i.get("contract_title") for i in goods_services if i.get("contract_title") is not None]
        contract_title.append(tender_instance.contract_title)
        contract_names = ", ".join(set(contract_title))
        contract_value_usd = sum(
            [i.get("contract_value_usd") for i in goods_services if i.get("contract_value_usd") is not None]
        )
        award_value_usd = sum(
            [i.get("award_value_usd") for i in goods_services if i.get("award_value_usd") is not None]
        )
        tender_value_usd = sum(
            [i.get("tender_value_usd") for i in goods_services if i.get("tender_value_usd") is not None]
        )
        contract_value_local = sum(
            [i.get("contract_value_local") for i in goods_services if i.get("contract_value_local") is not None]
        )
        award_value_local = sum(
            [i.get("award_value_local") for i in goods_services if i.get("award_value_local") is not None]
        )
        tender_value_local = sum(
            [i.get("tender_value_local") for i in goods_services if i.get("tender_value_local") is not None]
        )
        tender_instance.contract_title = contract_names
        tender_instance.contract_value_usd = contract_value_usd
        tender_instance.contract_value_local = contract_value_local
        tender_instance.tender_value_local = tender_value_local
        tender_instance.tender_value_usd = tender_value_usd
        tender_instance.award_value_local = award_value_local
        tender_instance.award_value_usd = award_value_usd
        tender_instance.save()
        good_services = tender_instance.goods_services.filter(country=country_obj)
        for good_service in good_services:
            for keyword in keywords:
                keyword_value = keyword.keyword
                if (
                    keyword_value in good_service.contract_title.strip()
                    or keyword_value in good_service.contract_desc.strip()
                ):
                    category = keyword.equity_category.category_name
                    instance = EquityCategory.objects.get(category_name=category)
                    tender_instance.equity_category.add(instance)
        process_redflag7.apply_async(args=(tender_instance.id,), queue="covid19")
        process_redflag6.apply_async(args=(tender_instance.id,), queue="covid19")
        process_redflag.apply_async(args=(tender_instance.id,), queue="covid19")
    instance = ScheduleRunner()
    instance.task_scheduler(
        task_name="evaluate_country_buyer",
        interval_name="every_hour",
        interval=8,
        country_alpha_code=country_obj.country_code_alpha_2,
    )
    instance.task_scheduler(
        task_name="evaluate_country_supplier",
        interval_name="every_hour",
        interval=8,
        country_alpha_code=country_obj.country_code_alpha_2,
    )
    management.call_command("export_summary_report")
