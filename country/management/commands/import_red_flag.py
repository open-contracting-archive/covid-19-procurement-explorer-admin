from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import gspread
from country.models import Country, Tender, EquityCategory, EquityKeywords, GoodsServices, RedFlag
from django.db.models import Q
from country.tasks import import_tender_data,fetch_equity_data,convert_local_to_usd,process_currency_conversion,process_redflag


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        print('Processing Red Flag in tender !!')
        tenders = Tender.objects.all()
        for tender in tenders:
            id = tender.id
            r = process_redflag.apply_async(args=(id,), queue='covid19')
            print('Created task for id :'+str(id))
        return "Done!!"