from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import gspread
from country.models import Country, Tender, EquityCategory, EquityKeywords, GoodsServices, RedFlag
from django.db.models import Q
from country.tasks import import_tender_data,fetch_equity_data,convert_local_to_usd,process_currency_conversion,process_redflag, clear_redflag


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        print('Removing all the relations of Red flag!!')
        tenders = Tender.objects.all()
        for tender in tenders:
            id = tender.id
            r = clear_redflag.apply_async(args=(id,), queue='covid19')
            
        print('All cleared !!')
        print('Processing Red Flag in tender !!')
        
        tender_instance = Tender.objects.filter(supplier__isnull=False,buyer__isnull=False).values('buyer__buyer_name','supplier__supplier_name')
        flag7_obj = RedFlag.objects.get(function_name='flag7')
        flag6_obj = RedFlag.objects.get(function_name='flag6')

        for instance in tender_instance:
            concentration = Tender.objects.filter(buyer__buyer_name=instance['buyer__buyer_name'],supplier__supplier_name=instance['supplier__supplier_name'])
            if len(concentration) > 10:    # supplier who has signed X(10) percent or more of their contracts with the same buyer (wins tenders from the same buyer);
                for i in concentration:
                    obj = Tender.objects.get(id=i.id)
                    obj.red_flag.add(flag7_obj)
        

        for tender in tender_instance:
            a = Tender.objects.values('buyer__buyer_name').filter(supplier__supplier_name=tender['supplier__supplier_name'],supplier__supplier_address=tender['supplier__supplier_address']).distinct('buyer__buyer_name')
            if len(a) > 2:
                if a[0]['buyer__buyer_name']==a[1]['buyer__buyer_name']:
                    for obj in a:
                        objs = Tender.objects.get(id=obj.id)
                        objs.red_flag.add(flag6_obj)


        for tender in tenders:
            id = tender.id
            r = process_redflag.apply_async(args=(id,), queue='covid19')
            print('Created task for id :'+str(id))
        return "Done!!"
