from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from country.models import Country, Tender,RedFlag,OverallSummary,TempDataImportTable
from django.db.models import Avg, Count, Min, Sum, Count,Window,Q
import xlsxwriter 


class Command(BaseCommand):
    help = 'Fix contract_status and contract_procedure fields!!'

    def handle(self, *args, **kwargs):
        print('Converting!!!!!!!!')
        tenders= Tender.objects.filter(link_to_contract='not_identified')

        for tender in tenders:
            print(tender.contract_id)
            temp_datas = TempDataImportTable.objects.filter(contract_id=tender.contract_id)
            if temp_datas:
                temp_value = temp_datas[0].procurement_process
                contract_status = temp_datas[0].contract_status
                link_to_contract = temp_datas[0].link_to_contract
                if tender.link_to_contract == 'not_identified':
                    tender.link_to_contract = link_to_contract
                if contract_status == 'not_identified':
                    contract_status_code = temp_datas[0].contract_status_code
                    if contract_status_code in ['Cancelled','Terminated','terminated']:
                        tender.status = 'cancelled'
                    elif contract_status_code in ['Active','active']:
                        tender.status = 'active'
                    else:
                        tender.status='not_identified'
                if temp_value in ['Direct','direct']:
                    temp_value = 'direct'
                elif temp_value in ['Limited','limited']:
                    temp_value ='limited'
                elif temp_value in ['Selective','selective']:
                    temp_value = 'selective'
                elif temp_value in ['Open','open']:
                    temp_value = 'open'
                else:
                    temp_value = 'not_identified'
                tender.procurement_procedure = temp_value
                tender.save()
                print("Tender value changed for id :"+str(tender.id))
        print('Done!!')