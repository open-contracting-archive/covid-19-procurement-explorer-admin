from content.models import DataImport
from django.db.models.signals import post_save
from django.dispatch import receiver
from country.tasks import store_in_temp_table

@receiver(post_save, sender=DataImport)
def validation_and_temp_table_store(sender,created ,instance, *args, **kwargs):
    if created:
        print("Data validation and temp table storage task started!")
        store_in_temp_table.apply_async(args=(instance.id,), queue='covid19')
