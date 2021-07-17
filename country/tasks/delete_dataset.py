from celery import Celery
from django.core import management

from country.models import Country, ImportBatch, TempDataImportTable, Tender
from visualization.helpers.scheduler import ScheduleRunner

app = Celery()


@app.task(name="delete_dataset")
def delete_dataset(data_import_id):
    import_batch = ImportBatch.objects.get(data_import_id=data_import_id)
    country_obj = Country.objects.filter(country_code_alpha_2=import_batch.country.country_code_alpha_2).first()
    all_temp_data_id = [i.id for i in import_batch.import_batch.all()]
    for temp_data_id in all_temp_data_id:
        obj = TempDataImportTable.objects.get(id=temp_data_id)
        tender_obj = Tender.objects.filter(temp_table_id=obj.id)
        obj.delete()
        tender_obj.delete()
        print("Done for temp data " + str(temp_data_id))
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
    management.call_command("export_summary_report", country_obj.country_code_alpha_2)
    return "Done"
