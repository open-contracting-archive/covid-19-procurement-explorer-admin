from celery import Celery
from django.core import management

from country.models import Country, ImportBatch, Tender
from libraries.scheduler import ScheduleRunner

app = Celery()


@app.task(name="delete_dataset")
def delete_dataset(data_import_id):
    import_batch = ImportBatch.objects.get(data_import_id=data_import_id)
    has_contracts = Tender.objects.filter(temp_table_id__import_batch=import_batch).exists()
    country = Country.objects.filter(country_code_alpha_2=import_batch.country.country_code_alpha_2).first()
    import_batch.delete()

    if has_contracts:
        run_post_delete(country)

    return "Done"


def run_post_delete(country):
    instance = ScheduleRunner()
    instance.task_scheduler(
        task_name="delete_unused_buyers",
        interval_name="every_hour",
        interval=2,
        country_alpha_code=country.country_code_alpha_2,
    )
    instance.task_scheduler(
        task_name="delete_unused_suppliers",
        interval_name="every_hour",
        interval=2,
        country_alpha_code=country.country_code_alpha_2,
    )
    instance.task_scheduler(
        task_name="evaluate_country_buyer",
        interval_name="every_hour",
        interval=2,
        country_alpha_code=country.country_code_alpha_2,
    )
    instance.task_scheduler(
        task_name="evaluate_country_supplier",
        interval_name="every_hour",
        interval=2,
        country_alpha_code=country.country_code_alpha_2,
    )

    # Clear cache table
    instance.task_scheduler(
        task_name="clear_cache_table",
        interval_name="round_minute",
        interval=5,
    )

    management.call_command("export_summary_report", country.country_code_alpha_2)
