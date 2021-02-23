from .models import Tender
from django.db.models import Avg, Count, Min, Sum, Count,Window

class RedFlags():
    def __init__(self):
        pass

    def flag1(self,contract_id):
        tender_instance = Tender.objects.get(id=contract_id)
        procurement_procedure = tender_instance.procurement_procedure
        no_of_bidders = tender_instance.no_of_bidders
        if procurement_procedure == "Direct" or no_of_bidders == 1:
            return True
        else:
            return False

    
    def flag4(self,contract_id):
        tender_instance = Tender.objects.filter(id=contract_id).aggregate(contract_value=Sum('goods_services__contract_value_usd'),tender_value=Sum('goods_services__tender_value_usd'))
        contract_value = tender_instance['contract_value']
        tender_value = tender_instance['tender_value']
        if contract_value > tender_value:
            return True
        else:
            return False


    def flag8(self,contract_id):     
        tender_instance = Tender.objects.filter(id=contract_id).aggregate(contract_value=Sum('goods_services__contract_value_usd'),tender_value=Sum('goods_services__tender_value_usd'))
        contract_value = tender_instance['contract_value']
        tender_value = tender_instance['tender_value']
        percentage_increase = ((contract_value - tender_value)/tender_value)*100
        if percentage_increase > 20:    #the difference between the expected purchase price and the final (contract) value exceeds 20 percent;
            return True
        else:
            return False
    
