import os

from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver

from content.models import DataImport
from country.tasks import delete_dataset
from covidadmin.constants import queues


@receiver(post_delete, sender=DataImport)
def delete_import_batch(sender, instance, *args, **kwargs):
    delete_dataset.apply(args=(instance.page_ptr_id,), queue=queues.default)

    # Delete dataset file
    filename = instance.import_file.name
    file_path = settings.MEDIA_ROOT + "/" + str(filename)
    os.remove(file_path)
