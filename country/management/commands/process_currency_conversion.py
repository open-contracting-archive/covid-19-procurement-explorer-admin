from django.core.management.base import BaseCommand
from django.db.models import Q

from country.models import Country, GoodsServices
from country.tasks import process_currency_conversion


class Command(BaseCommand):
    help = "Convert contract local amount values into USD"

    def handle(self, *args, **kwargs):
        self.stdout.write("Processing currency conversion")
        countries = Country.objects.exclude(country_code_alpha_2="gl").all()

        for country in countries:
            goods_services_items = GoodsServices.objects.filter(
                Q(tender_value_usd__isnull=True) | Q(award_value_usd__isnull=True) | Q(contract_value_usd__isnull=True)
            )
            self.stdout.write(country.name + " Found: " + str(goods_services_items.count()))

            for goods_services_obj in goods_services_items:
                tender_date = goods_services_obj.contract.contract_date
                process_currency_conversion.apply_async(
                    args=(goods_services_obj.id, tender_date, country.currency),
                    queue="covid19",
                )
                self.stdout.write("Created task for id :" + str(goods_services_obj.id))

        self.stdout.write("Done")
