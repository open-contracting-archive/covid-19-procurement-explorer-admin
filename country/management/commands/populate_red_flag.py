from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import gspread
from country.models import Country, Tender,RedFlag




class Command(BaseCommand):
    help = 'Import Red Flag'

    def handle(self, *args, **kwargs):
        red_flags = [{"title":"Direct contract or single bid received","description":"Tender was direct or had a single bidder.  Note: in the context of an emergency direct contracts can be justified.","function_name":"flag1","implemented":True},
                    {"title":"Contract value is higher or lower than average for this item category","description":"Contract value is threshold distance from mean for item category.  Flag contract if price is higher than average for a particular item category.","function_name":"flag2","implemented":False},
                    {"title":"Supplier wins contract for item or service types it is unlikely to have, or higher quantitities of items or services it is unlikely to be able to provide","description":"The items won do not match the description or quantity historically provided by supplier","function_name":"flag3","implemented":False},
                    {"title":"Contract value is higher than tender value","description":"Contract value is higher than tender value","function_name":"flag4","implemented":True},
                    {"title":"Contract is awarded to supplier that has won a disproportionate number of contracts of the same type","description":"Supplier wins 2+ (higher than average value or number of contracts can be used) contracts from same buyer, of similar size and similar item via same procurement type","function_name":"flag5","implemented":False},
                    {"title":"Contract is awarded to supplier that has similar information (address, number, legal representative) to other suppliers for the same buyer","description":"Supplier 1 info matches supplier 2 info for the same buyer.","function_name":"flag6","implemented":True},
                    {"title":"Concentration","description":"Supplier who has signed X percent or more of their contracts with the same buyer (wins tenders from the same buyer);","function_name":"flag7","implemented":True},
                    {"title":"High price dynamics","description":"The difference between the expected purchase price and the final (contract) value exceeds 20 percent;","function_name":"flag8","implemented":True},
                    {"title":"Framework agreement with several tenderers (with less than 3 tenderers participating)","description":"","function_name":"flag9","implemented":False},
                    {"title":"High contract value","description":"High contract value can be considered as a risk indicator","function_name":"flag10","implemented":False}
                   ]
        print('Importingg!!!!!!!!')
        try:
            for values in red_flags:
                obj , created = RedFlag.objects.get_or_create(title=values['title'],description=values['description'],function_name=values['function_name'])
                if obj:
                    obj.implemented = values['implemented']
                    obj.save()
                print(f'Created : {obj}, {created}')
        except Exception as e:
            print(e)
True