from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import gspread
from country.models import Country, Tender, EquityCategory, EquityKeywords, GoodsServices, RedFlag
from django.db.models import Q
from country.tasks import import_tender_data,fetch_equity_data,convert_local_to_usd,process_currency_conversion,process_redflag, clear_redflag, process_redflag7,process_redflag6


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        print('Removing all the relations of Red flag!!')
        tenders = Tender.objects.all()
        for tender in tenders:
            id = tender.id
            a = clear_redflag.apply_async(args=(id,), queue='covid19')
            
        print('All cleared !!')
        print('Processing Red Flag in tender !!')
        
        tender_instance = Tender.objects.filter(supplier__isnull=False,buyer__isnull=False).values('id','buyer__buyer_name','supplier__supplier_name','supplier__supplier_address')
        for tender in tender_instance:
            id = tender['id']
            b = process_redflag7.apply_async(args=(id,tender), queue='covid19')
            c = process_redflag6.apply_async(args=(id,tender), queue='covid19')
        
        for tender in tenders:
            id = tender.id
            r = process_redflag.apply_async(args=(id,), queue='covid19')
            print('Created task for id :'+str(id))
        return "Done!!"
