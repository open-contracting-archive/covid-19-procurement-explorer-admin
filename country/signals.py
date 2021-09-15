from django.db.models.signals import post_save
from django.dispatch import receiver

from country.models import GoodsServices
from country.tasks import update_contract_attributes
from covidadmin.constants import queues


@receiver(post_save, sender=GoodsServices)
def update_contract(sender, instance, *args, **kwargs):
    update_contract_attributes.apply_async(args=(instance.contract_id,), queue=queues.default)
