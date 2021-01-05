from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import gspread
from country.models import Country, Tender, EquityCategory, EquityKeywords, GoodsServices
from django.db.models import Q
from country.tasks import import_tender_data,fetch_equity_data,convert_local_to_usd,process_currency_conversion


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        print('Processing currency conversion !!')
        unconverted_tender = GoodsServices.objects.filter(Q(tender_value_usd__isnull=True)| Q(award_value_usd__isnull=True) | Q(contract_value_usd__isnull=True))
        for tender in unconverted_tender:
            tender_value_local = tender.tender_value_local
            tender_date =  tender.contract.contract_date
            currency = tender.country.currency
            id = tender.id
            contract_value_local = tender.contract_value_local
            award_value_local = tender.award_value_local
            r = process_currency_conversion.apply_async(args=(tender_value_local,award_value_local,contract_value_local,tender_date,currency,id), queue='covid19')
            print('Created task for id :'+str(id))
        return "Done!!"