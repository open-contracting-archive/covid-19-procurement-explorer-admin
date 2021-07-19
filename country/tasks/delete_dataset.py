from celery import Celery
from django.core import management

from country.models import Country, ImportBatch
from visualization.helpers.scheduler import ScheduleRunner

app = Celery()


@app.task(name="delete_dataset")
def delete_dataset(data_import_id):
    import_batch = ImportBatch.objects.get(data_import_id=data_import_id)
    country_obj = Country.objects.filter(country_code_alpha_2=import_batch.country.country_code_alpha_2).first()
    import_batch.delete()

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
    instance.task_scheduler(
        task_name="delete_unused_buyers",
        interval_name="every_hour",
        interval=8,
        country_alpha_code=country_obj.country_code_alpha_2,
    )
    instance.task_scheduler(
        task_name="delete_unused_suppliers",
        interval_name="every_hour",
        interval=8,
        country_alpha_code=country_obj.country_code_alpha_2,
    )
    management.call_command("export_summary_report", country_obj.country_code_alpha_2)

    return "Done"
