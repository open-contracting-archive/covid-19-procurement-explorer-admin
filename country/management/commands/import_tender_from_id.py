from django.core.management.base import BaseCommand
from country.models import Country
from country.tasks import import_tender_from_batch_id


class Command(BaseCommand):
    help = "Import tender from data temp table file"

    def add_arguments(self, parser):
        parser.add_argument("country", type=str, help="Country to import tender")
        parser.add_argument("batch_id", type=str, help="Import Batch Id")

    def handle(self, *args, **kwargs):
        country = kwargs["country"]
        batch_id = kwargs["batch_id"]
        print(f"Fetching tender data for Batch id {batch_id} for country {country}")

        try:
            result = Country.objects.filter(name=country).first()
            country = result.name
            currency = result.currency

            if not result:
                print(f'Country "{country}" does not exists in our database.')
            else:
                r = import_tender_from_batch_id.apply_async(args=(batch_id, country, currency), queue="covid19")
                print("Created task: import_tender_from_batch_id")
        except Exception as e:
            print(e)
