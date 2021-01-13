from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from .serializers import TenderSerializer
import operator
from functools import reduce
import datetime 
import dateutil.relativedelta
from django.db.models import Avg, Count, Min, Sum, Count,Window
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
import math
from collections import defaultdict

from country.models import Tender,Country,CovidMonthlyActiveCases, GoodsServices, GoodsServicesCategory, Supplier, Buyer, EquityCategory
import itertools
from country.models import Tender,Country,CovidMonthlyActiveCases, GoodsServices
from content.models import CountryPartner
import itertools, json

def add_filter_args(filter_type,filter_value,filter_args):
    if filter_value != 'notnull':
        filter_args[f'{filter_type}__id'] = filter_value
    else:
        filter_args[f'{filter_type}__isnull'] = False
    return filter_args

class TotalSpendingsView(APIView):
    def get(self,request):
        """
        Return a list of all contracts.
        """
        #Calculating total tender
        country =  self.request.GET.get('country',None)
        buyer = self.request.GET.get('buyer')
        supplier = self.request.GET.get('supplier')
        today = datetime.datetime.now()
        one_month_earlier = today + dateutil.relativedelta.relativedelta(months=-1)
        earlier = one_month_earlier.replace(day=1).date()
        filter_args = {}
        if country: filter_args['country__country_code_alpha_2'] = country
        if buyer: filter_args = add_filter_args('buyer',buyer,filter_args)
        if supplier: filter_args = add_filter_args('supplier',supplier,filter_args)

        total_country_tender_amount = Tender.objects.filter(**filter_args).aggregate(Sum('goods_services__contract_value_usd'))
        total_country_tender_local_amount = Tender.objects.filter(**filter_args).aggregate(Sum('goods_services__contract_value_local'))
        this_month = Tender.objects.filter(**filter_args,contract_date__year=today.year,
                        contract_date__month=today.month).aggregate(Sum('contract_value_usd'))
        this_month_local = Tender.objects.filter(**filter_args,contract_date__year=today.year,
                        contract_date__month=today.month).aggregate(Sum('contract_value_local'))
        earlier_month = Tender.objects.filter(**filter_args,contract_date__year=earlier.year,
                        contract_date__month=earlier.month).aggregate(Sum('contract_value_usd'))
        earlier_month_local = Tender.objects.filter(**filter_args,contract_date__year=earlier.year,
                        contract_date__month=earlier.month).aggregate(Sum('contract_value_local'))
        try:
            increment = ((this_month['contract_value_usd__sum'] - earlier_month['contract_value_usd__sum'])/earlier_month['contract_value_usd__sum'])*100
            increment_local = ((this_month_local['contract_value_local__sum'] - earlier_month_local['contract_value_local__sum'])/earlier_month_local['contract_value_usd__sum'])*100
        except Exception:
            increment =0
            increment_local = 0
        except ZeroDivisionError:
            increment = 0
            increment_local = 0
        bar_chart =Tender.objects.filter(**filter_args).values('procurement_procedure').annotate(sum=Sum('contract_value_usd'))
        bar_chart_local = Tender.objects.filter(**filter_args).values('procurement_procedure').annotate(sum=Sum('contract_value_local'))
        selective_sum=0
        limited_sum=0
        open_sum=0
        selective_sum_local=0
        limited_sum_local=0
        open_sum_local=0
        direct_sum_local=0
        limited_total=0
        open_total= 0
        selective_total=0
        direct_total=0
        
        for i in bar_chart:
            if i['procurement_procedure']=='selective':
                selective_total = i['sum']
            elif i['procurement_procedure']=='limited':
                limited_total = i['sum']
            elif i['procurement_procedure']=='open':
                open_total = i['sum']
            elif i['procurement_procedure']=='direct':
                direct_total = i['sum']
        for i in bar_chart_local:
            if i['procurement_procedure']=='selective':
                selective_sum_local = i['sum']
            elif i['procurement_procedure']=='limited':
                limited_sum_local = i['sum']
            elif i['procurement_procedure']=='open':
                open_sum_local = i['sum']
            elif i['procurement_procedure']=='direct':
                direct_sum_local = i['sum']
        line_chart = Tender.objects.filter(**filter_args).annotate(month=TruncMonth('contract_date')).values('month').annotate(total=Sum('contract_value_usd')).order_by("-month")
        line_chart_local = Tender.objects.filter(**filter_args).annotate(month=TruncMonth('contract_date')).values('month').annotate(total=Sum('contract_value_local')).order_by("-month")

        line_chart_local_list = []
        line_chart_list = []
        for i in line_chart:
            a= {}
            a['date']= i['month']
            a['value'] = i['total']
            line_chart_list.append(a)
        for i in line_chart_local:
            a= {}
            a['date']= i['month']
            a['value'] = i['total']
            line_chart_local_list.append(a)
        result = {'usd':{'total':total_country_tender_amount['goods_services__contract_value_usd__sum'],
                    'increment':increment,
                    "line_chart" : line_chart_list,
                    'bar_chart':[{
                            "method":"open",
                            "value":open_total
                            },
                        {
                            "method":"limited",
                            "value":limited_total
                            },
                        {
                            "method":"selective",
                            "value":selective_total
                            },
                        {
                            "method":"direct",
                            "value":direct_total
                        }],},
                'local':{
                'total':total_country_tender_local_amount['goods_services__contract_value_local__sum'],
                    'increment':increment_local,
                    "line_chart" : line_chart_local_list,
                    'bar_chart':[{
                            "method":"open",
                            "value":open_sum_local
                            },
                        {
                            "method":"limited",
                            "value":limited_sum_local
                            },
                        {
                            "method":"selective",
                            "value":selective_sum_local
                            },
                        {
                            "method":"direct",
                            "value":direct_sum_local
                        }]
            }
        
        }
        
        return JsonResponse(result)


class TotalContractsView(APIView):
    def get(self,request):
        """
        Return a list of all contracts.
        """
        # Calculating total tender
        country =  self.request.GET.get('country',None)
        buyer = self.request.GET.get('buyer')
        supplier = self.request.GET.get('supplier')
        today = datetime.datetime.now()
        one_month_earlier = today + dateutil.relativedelta.relativedelta(months=-1)
        earlier = one_month_earlier.replace(day=1).date()
        open_count = 0
        selective_count = 0
        direct_count =0
        limited_count=0
        filter_args = {}
        if country: filter_args['country__country_code_alpha_2'] = country
        if buyer: filter_args = add_filter_args('buyer',buyer,filter_args)
        if supplier: filter_args = add_filter_args('supplier',supplier,filter_args)

        total_country_tender = Tender.objects.filter(**filter_args).count()
        this_month = Tender.objects.filter(**filter_args,contract_date__year=today.year,
                        contract_date__month=today.month).count()
        earlier_month = Tender.objects.filter(**filter_args,contract_date__year=earlier.year,
                        contract_date__month=earlier.month).count()
        try:
            difference = ((this_month-earlier_month)/earlier_month)*100
        except ZeroDivisionError:
            difference = 0
        bar_chart =Tender.objects.filter(**filter_args).values('procurement_procedure').annotate(count=Count('procurement_procedure'))
        for i in bar_chart:
            if i['procurement_procedure']=='selective':
                selective_count = i['count']
            elif i['procurement_procedure']=='limited':
                limited_count = i['count']
            elif i['procurement_procedure']=='open':
                open_count = i['count']
            elif i['procurement_procedure']=='direct':
                direct_count = i['count']
        line_chart = Tender.objects.filter(**filter_args).annotate(month=TruncMonth('contract_date')).values('month').annotate(total=Count('id')).order_by("-month")
        line_chart_list = []
        for i in line_chart:
            a= {}
            a['date']= i['month']
            a['value'] = i['total']
            line_chart_list.append(a)
        result = {'total':total_country_tender,
                    'difference':difference,
                    "line_chart" : line_chart_list,
                    'bar_chart':[{
                            "method":"open",
                            "value":open_count
                            },
                        {
                            "method":"limited",
                            "value":limited_count
                            },
                        {
                            "method":"selective",
                            "value":selective_count
                            },
                        {
                            "method":"direct",
                            "value":direct_count
                        }]
                    }
        return JsonResponse(result)


class AverageBidsView(APIView):
    def get(self,request):
        """
        Returns average bids for contracts
        """
        country =  self.request.GET.get('country',None)
        buyer = self.request.GET.get('buyer')
        current_time = datetime.datetime.now()
        previous_month_date = current_time - dateutil.relativedelta.relativedelta(months=-1)
        previous_month = previous_month_date.replace(day=1).date()
        filter_args = {}
        if country: filter_args['country__country_code_alpha_2'] = country
        if buyer: filter_args = add_filter_args('buyer',buyer,filter_args)

        # Month wise average of number of bids for contracts
        monthwise_data_count = Tender.objects.filter(**filter_args).annotate(month=TruncMonth('contract_date')).values('month').annotate(count=Count('id')).order_by("-month")
        monthwise_data_sum = Tender.objects.filter(**filter_args).annotate(month=TruncMonth('contract_date')).values('month').annotate(sum=Sum("goods_services__no_of_bidders")).order_by("-month")
        final_line_chart_data = [{'date': monthwise_data_sum[i]['month'],'value': round(monthwise_data_sum[i]['sum']/monthwise_data_count[i]['count']) if monthwise_data_sum[i]['sum'] else 0} for i in range(len(monthwise_data_sum))]
        
        # Difference percentage calculation
        try:
            dates_in_line_chart = [i['date'] for i in final_line_chart_data]
            final_current_month_avg = [final_line_chart_data[0]['value'] if current_time.replace(day=1).date() in dates_in_line_chart else 0]
            final_previous_month_avg = [final_line_chart_data[1]['value'] if previous_month in dates_in_line_chart else 0]
            difference = round((( final_current_month_avg[0] - final_previous_month_avg[0])/final_previous_month_avg[0])*100)
        except:
            difference = 0
        
        # Overall average number of bids for contracts
        overall_avg = Tender.objects.filter(**filter_args).aggregate(sum=Sum('goods_services__no_of_bidders'))
        overall_avg_count = Tender.objects.filter(**filter_args).count()
        result ={
            'average' : round(overall_avg['sum']/overall_avg_count) if overall_avg['sum'] else 0,
            'difference' : difference,
            'line_chart' : final_line_chart_data
        }
        return JsonResponse(result)
        

class GlobalOverView(APIView):
    def get(self,request):
        temp={}
        tender_temp ={}
        data=[]
        count = Tender.objects.annotate(month=TruncMonth('contract_date')).values('month').annotate(total_contract=Count('id'),total_amount=Sum('goods_services__contract_value_usd')).order_by("month")
        countries = Country.objects.all()
        for i in count:
            result={}
            end_date = i['month'] + dateutil.relativedelta.relativedelta(months=1)
            start_date=i['month']
            result["details"]=[]
            result["month"]=str(start_date.year)+'-'+str(start_date.month)
            for j in countries:
                b={}
                tender_count =Tender.objects.filter(country__country_code_alpha_2=j.country_code_alpha_2,contract_date__gte=start_date,contract_date__lte=end_date).count()
                tender =  Tender.objects.filter(country__country_code_alpha_2=j.country_code_alpha_2,contract_date__gte=start_date,contract_date__lte=end_date).aggregate(Sum('goods_services__contract_value_usd'))
                b['country']=j.name
                b['country_code']=j.country_code_alpha_2
                b['country_continent']=j.continent
                if tender['goods_services__contract_value_usd__sum']==None:
                    tender_val = 0
                else:
                    tender_val = tender['goods_services__contract_value_usd__sum']
                if tender_count==None:
                    contract_val = 0
                else:
                    contract_val = tender_count
                if bool(temp) and j.name in temp.keys():
                    current_val = temp[j.name]
                    cum_value =current_val+tender_val
                    temp[j.name]=cum_value
                    b['amount_usd'] = cum_value
                else:
                    temp[j.name] = tender_val
                    b['amount_usd'] = tender_val
                if bool(tender_temp) and j.name in tender_temp.keys():
                    current_val = tender_temp[j.name]
                    cum_value =current_val+contract_val
                    tender_temp[j.name]=cum_value
                    b['tender_count'] = cum_value
                else:
                    tender_temp[j.name] = contract_val
                    b['tender_count'] = contract_val
                result["details"].append(b)
            data.append(result)
        final={"result":data}
        return JsonResponse(final)


class TopSuppliers(APIView):
    def get(self,request):
        country =  self.request.GET.get('country',None)
        buyer = self.request.GET.get('buyer')
        filter_args = {}
        if country: filter_args['country__country_code_alpha_2'] = country
        if buyer: filter_args = add_filter_args('buyer',buyer,filter_args)
        filter_args['supplier__isnull']=False
        filter_args['goods_services__contract_value_usd__isnull']=False
        for_value = Tender.objects.filter(**filter_args).values('supplier__id','supplier__supplier_name','country__currency')\
                    .annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local')).exclude(usd__isnull=True).order_by('-usd')[:10]
        for_number = Tender.objects.filter(**filter_args).values('supplier__id','supplier__supplier_name','country__currency')\
                        .annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local')).exclude(usd__isnull=True).order_by('-count')[:10]
        by_number= []
        by_value = []
    
        for value in for_value:
            a= {}
            a["amount_local"] = value['local'] if value['local'] else 0
            a["amount_usd"] = value['usd'] if value['usd'] else 0
            a["local_currency_code"] = value['country__currency']
            a['supplier_id'] = value['supplier__id']
            a['supplier_name'] = value['supplier__supplier_name']
            a['tender_count'] = value['count']
            by_value.append(a)
        for value in for_number:
            a= {}
            a["amount_local"] = value['local'] if value['local'] else 0
            a["amount_usd"] = value['usd'] if value['usd'] else 0
            a["local_currency_code"] = value['country__currency']
            a['supplier_id'] = value['supplier__id']
            a['supplier_name'] = value['supplier__supplier_name']
            a['tender_count'] = value['count']
            by_number.append(a)
        result={"by_number": by_number,
                "by_value": by_value}
        return JsonResponse(result)


class TopBuyers(APIView):
    def get(self,request):
        country =  self.request.GET.get('country',None)
        supplier = self.request.GET.get('supplier')

        filter_args = {}
        if country: filter_args['country__country_code_alpha_2'] = country
        if supplier: filter_args = add_filter_args('supplier',supplier,filter_args)
        filter_args['buyer__isnull']=False
        filter_args['goods_services__contract_value_usd__isnull']=False
        for_value = Tender.objects.filter(**filter_args).values('buyer__id','buyer__buyer_name','country__currency')\
                    .annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local')).order_by('-usd')[:10]
        for_number = Tender.objects.filter(**filter_args).values('buyer__id','buyer__buyer_name','country__currency')\
                        .annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local')).order_by('-count')[:10]
        by_number= []
        by_value = []
        for value in for_value:
            a= {}
            a["amount_local"] = value['local'] if value['usd'] else 0
            a["amount_usd"] = value['usd'] if value['usd'] else 0
            a["local_currency_code"] = value['country__currency']
            a['buyer_id'] = value['buyer__id']
            a['buyer_name'] = value['buyer__buyer_name']
            a['tender_count'] = value['count']
            by_value.append(a)
        for value in for_number:
            a= {}
            a["amount_local"] = value['local'] if value['usd'] else 0
            a["amount_usd"] = value['usd'] if value['usd'] else 0
            a["local_currency_code"] = value['country__currency']
            a['buyer_id'] = value['buyer__id']
            a['buyer_name'] = value['buyer__buyer_name']
            a['tender_count'] = value['count']
            by_number.append(a)
        result={"by_number": by_number,
                "by_value": by_value}
        return JsonResponse(result)


class DirectOpen(APIView):
    def get(self,request):
        country =  self.request.GET.get('country',None)
        buyer = self.request.GET.get('buyer')
        supplier = self.request.GET.get('supplier')
        filter_args = {}
        if buyer: filter_args = add_filter_args('buyer',buyer,filter_args)
        if supplier: filter_args = add_filter_args('supplier',supplier,filter_args)

        if country:
            amount_direct = Tender.objects.filter(country__country_code_alpha_2=country, procurement_procedure='direct').values('country__currency').annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local'))
            amount_open = Tender.objects.filter(country__country_code_alpha_2=country, procurement_procedure='open').values('country__currency').annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local'))
        elif buyer or supplier:
            amount_direct = Tender.objects.filter(**filter_args,procurement_procedure='direct').values('procurement_procedure').annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local'))
            amount_open = Tender.objects.filter(**filter_args,procurement_procedure='open').values('procurement_procedure').annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local'))
        else:
            amount_direct = Tender.objects.filter(procurement_procedure='direct').values('procurement_procedure').annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local'))
            amount_open = Tender.objects.filter(procurement_procedure='open').values('procurement_procedure').annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local'))

        country_currency = []
        if country:
            country_obj = Country.objects.filter(name=country)
            if country_obj: country_currency = country_obj.currency
        if amount_direct:
            for i in amount_direct:
                result_direct ={"amount_local" : i['local'] if i['local'] else 0,
                                "amount_usd": i['usd'] if i['usd'] else 0,
                                "tender_count": i['count'],
                                "local_currency_code":i['country__currency'] if 'country__currency' in i else [],
                                "procedure": "direct"
                }
        else:
            result_direct ={    "amount_local" : 0,
                                "amount_usd": 0,
                                "tender_count": 0,
                                "local_currency_code": country_currency,
                                "procedure": "direct"
                }            

        if amount_open:
            for i in amount_open:
                result_open ={ "amount_local" : i['local'] if i['local'] else 0,
                            "amount_usd": i['usd'] if i['usd'] else 0,
                            "tender_count": i['count'],
                            "local_currency_code":i['country__currency'] if 'country__currency' in i else [],
                            "procedure": "open"
                }
        else:
            result_open ={    
                               "amount_local" : 0,
                                "amount_usd": 0,
                                "tender_count": 0,
                                "local_currency_code":country_currency,
                                "procedure": "open"
                } 
        
        result = [result_direct,result_open]

        return JsonResponse(result,safe=False)


class ContractStatusView(APIView):
    """
       Returns status wise grouped info about contracts 
    """
    def get(self,request):
        filter_args = {}
        result = list()
        currency_code = ''
        status = ['active','completed','cancelled']
        country =  self.request.GET.get('country',None)
        buyer = self.request.GET.get('buyer')
        
        if country: filter_args['country__country_code_alpha_2'] = country
        if buyer: filter_args = add_filter_args('buyer',buyer,filter_args)

        # Status code wise grouped sum of contract value
        contract_value_local_sum = Tender.objects.filter(**filter_args).values('status').annotate(sum=Sum('goods_services__contract_value_local'))
        contract_value_usd_sum = Tender.objects.filter(**filter_args).values('status').annotate(sum=Sum('goods_services__contract_value_usd'))

        # Status code wise grouped total number of contracts
        grouped_contract_no = Tender.objects.filter(**filter_args).values('status').annotate(count=Count('id'))

        if country: 
            try:
                country_res = Country.objects.get(name=country)
                currency_code = country_res.currency
            except Exception as e:
                print(e)
                
        status_in_result = [i['status'] for i in contract_value_local_sum]
        for i in range(len(status)):
            if status[i] in status_in_result:
                result.append(
                    {
                        "amount_local": [each['sum'] if each['sum'] else 0 for each in contract_value_local_sum if status[i] == each['status']][0],
                        "amount_usd": [each['sum'] if each['sum'] else 0 for each in contract_value_usd_sum if status[i] == each['status']][0],
                        "tender_count": [each['count'] if each['count'] else 0 for each in grouped_contract_no if status[i] == each['status']][0],
                        "local_currency_code": currency_code ,
                        "status": status[i]
                    }
                    )
            else:
                result.append(
                    {
                        "amount_local": 0,
                        "amount_usd": 0,
                        "tender_count": 0,
                        "local_currency_code": currency_code,
                        "status": status[i]
                    }
                    )

        return JsonResponse(result,safe=False)


class QuantityCorrelation(APIView):
    today = datetime.datetime.now()
    def get(self,request):
        country =  self.request.GET.get('country',None)
        if country:
            contracts_quantity = Tender.objects.filter(country__country_code_alpha_2=country).annotate(month=TruncMonth('contract_date')).values('month','country__currency').annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local')).order_by('-month')
        else:
            contracts_quantity = Tender.objects.annotate(month=TruncMonth('contract_date')).values('month').annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd')).order_by('-month')
        
        contracts_quantity_list = []
        
        for i in contracts_quantity:
            if country:
                active_case = CovidMonthlyActiveCases.objects.filter(country__country_code_alpha_2 = country, covid_data_date__year=i['month'].year, covid_data_date__month=i['month'].month).values('active_cases_count')
            else :
                active_case = CovidMonthlyActiveCases.objects.filter(covid_data_date__year=i['month'].year, covid_data_date__month=i['month'].month).values('active_cases_count')
            active_case_count = 0
            try:
                for j in active_case:
                    if j['active_cases_count']:
                        active_case_count += j['active_cases_count']
            except Exception:
                active_case_count = 0
            a = {}
            a["active_cases"] = active_case_count
            a["amount_local"] = i['local'] if 'local' in i else ''
            a["amount_usd"] = i['usd']
            a["local_currency_code"] = i['country__currency'] if 'country__currency' in i else ''
            a["month"] = i['month']
            a["tender_count"] = i['count']
            contracts_quantity_list.append(a)

        return JsonResponse(contracts_quantity_list, safe= False) 

class MonopolizationView(APIView):
    def get(self,request):
        filter_args = {}
        country =  self.request.GET.get('country',None)
        buyer = self.request.GET.get('buyer')
        if country: filter_args['country__country_code_alpha_2'] = country
        if buyer: filter_args = add_filter_args('buyer',buyer,filter_args)

        current_time = datetime.datetime.now()
        previous_month_date = current_time - dateutil.relativedelta.relativedelta(months=-1)
        previous_month = previous_month_date.replace(day=1).date()

        # Month wise average of number of bids for contracts
        monthwise_data_contracts = Tender.objects.filter(**filter_args).annotate(month=TruncMonth('contract_date')).values('month').annotate(count=Count('id')).order_by("-month")
        monthwise_data_suppliers = Tender.objects.filter(**filter_args).annotate(month=TruncMonth('contract_date')).values('month').annotate(count=Count('supplier__supplier_id',distinct=True)).order_by("-month")
        final_line_chart_data = [{'date': monthwise_data_contracts[i]['month'],'value': round(monthwise_data_contracts[i]['count']/monthwise_data_suppliers[i]['count']) if monthwise_data_contracts[i]['count'] and monthwise_data_suppliers[i]['count']  else 0} for i in range(len(monthwise_data_contracts))]

        # Difference percentage calculation
        try:
            dates_in_line_chart = [i['date'] for i in final_line_chart_data]
            final_current_month_avg = [final_line_chart_data[0]['value'] if current_time.replace(day=1).date() in dates_in_line_chart else 0]
            final_previous_month_avg = [final_line_chart_data[1]['value'] if previous_month in dates_in_line_chart else 0]
            difference = round((( final_current_month_avg[0] - final_previous_month_avg[0])/final_previous_month_avg[0])*100)
        except:
            difference = 0

        # Overall average number of bids for contracts
        overall_contracts = Tender.objects.filter(**filter_args).aggregate(count=Count('id'))
        overall_suppliers = Tender.objects.filter(**filter_args).aggregate(count=Count('supplier__supplier_id',distinct=True))

        result ={
            'average' : round(overall_contracts['count']/overall_suppliers['count']) if overall_contracts['count'] and overall_suppliers['count'] else 0,
            'difference' : difference,
            'line_chart' : final_line_chart_data
        }
        return JsonResponse(result)

class CountrySuppliersView(APIView):
    def get(self,request):
        filter_args = {}
        country =  self.request.GET.get('country',None)
        if country: filter_args['country__country_code_alpha_2'] = country
        tender_amounts_buyer = Tender.objects.filter(**filter_args,buyer__isnull=False,goods_services__goods_services_category__isnull=False).values('goods_services__goods_services_category__id','goods_services__goods_services_category__category_name','buyer__id','buyer__buyer_name').annotate(local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd'),count=Count('id'))

        tender_amounts_supplier = Tender.objects.filter(**filter_args,supplier__isnull=False,goods_services__goods_services_category__isnull=False).values('supplier__id','supplier__supplier_name','goods_services__goods_services_category__id','goods_services__goods_services_category__category_name').annotate(local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd'),count=Count('id'))
        result = {
            'product_buyer' : [
                {
                "amount_local": tender_amounts_buyer[i]['local'],
                "amount_usd": tender_amounts_buyer[i]['usd'],
                "buyer_id": tender_amounts_buyer[i]['buyer__id'],
                "buyer_name": tender_amounts_buyer[i]['buyer__buyer_name'],
                "product_id": tender_amounts_buyer[i]['goods_services__goods_services_category__id'],
                "product_name": tender_amounts_buyer[i]['goods_services__goods_services_category__category_name'],
                "tender_count": tender_amounts_buyer[i]['count']
                }
                for i in range(len(tender_amounts_buyer))
            ],
            'supplier_product' : [
                {  
                "amount_local": tender_amounts_supplier[i]['local'],
                "amount_usd": tender_amounts_supplier[i]['usd'],
                "product_id": tender_amounts_supplier[i]['goods_services__goods_services_category__id'],
                "product_name": tender_amounts_supplier[i]['goods_services__goods_services_category__category_name'],
                "supplier_id": tender_amounts_supplier[i]['supplier__id'],
                "supplier_name": tender_amounts_supplier[i]['supplier__supplier_name'],
                "tender_count": tender_amounts_supplier[i]['count']
                }
                for i in range(len(tender_amounts_supplier))
            ]
        }
        
        return JsonResponse(result)

class CountryMapView(APIView):
    def get(self,request):
        country =  self.request.GET.get('country',None)
        try:
            country_instance = Country.objects.get(country_code_alpha_2=country)
        except Exception as DoesNotExist:
            final={"result":"Invalid Alpha Code"}
            return JsonResponse(final)
        if country != None and country_instance !=None:
            tender_instance = Tender.objects.filter(country__country_code_alpha_2=country).aggregate(total_usd=Sum('goods_services__contract_value_usd'),total_local=Sum('goods_services__contract_value_local'))
            count = Tender.objects.filter(country__country_code_alpha_2=country).count()
            final={}
            final['country_code']=country_instance.country_code_alpha_2
            final['country'] = country_instance.name
            final['country_continent']=country_instance.continent
            final['amount_usd'] = tender_instance['total_usd']
            final['amount_local'] = tender_instance['total_local']
            final['tender_count'] = count    
        else:
            final={"result":"Invalid Alpha Code"}
        return JsonResponse(final)


class WorldMapView(APIView):
    def get(self,request):
        country_instance = Country.objects.all()
        result = []
        for country in country_instance:
            data = {}
            tender_instance = Tender.objects.filter(country=country).aggregate(total_usd=Sum('goods_services__contract_value_usd'))
            tender_count = Tender.objects.filter(country=country).count()
            data['country_code']=country.country_code_alpha_2
            data['country'] = country.name
            data['country_continent']=country.continent
            data['amount_usd'] = tender_instance['total_usd']
            data['tender_count'] = tender_count
            result.append(data)
        final_result = {"result":result}
        return JsonResponse(final_result)
        
class GlobalSuppliersView(APIView):
    def get(self,request):
        supplier =  self.request.GET.get('supplier',None)
        product =  self.request.GET.get('product',None)
        usd_amountwise_sorted =  Tender.objects.filter(supplier__isnull=False,goods_services__goods_services_category__isnull=False).values('supplier__supplier_id','goods_services__goods_services_category__id').annotate(usd=Sum('goods_services__contract_value_usd')).exclude(usd__isnull=True).order_by('-usd')
        countwise_sorted = Tender.objects.filter(supplier__isnull=False,goods_services__goods_services_category__isnull=False).values('supplier__supplier_id','goods_services__goods_services_category__id').annotate(count=Count('id')).exclude(count__isnull=True).order_by('-count')
        suppliers_dict = defaultdict(lambda : {'countwise':[],'amountwise' : []}) 

        for i in usd_amountwise_sorted:
            if len(suppliers_dict[i['goods_services__goods_services_category__id']]['amountwise']) <= 5:
                suppliers_dict[i['goods_services__goods_services_category__id']]['amountwise'].append(i['supplier__supplier_id']) 
        for i in countwise_sorted:
            if len(suppliers_dict[i['goods_services__goods_services_category__id']]['countwise']) <= 5:
                suppliers_dict[i['goods_services__goods_services_category__id']]['countwise'].append(i['supplier__supplier_id']) 
        if supplier:
            final_suppliers_list_countwise = [supplier]
            final_suppliers_list_amountwise = [supplier]
        else:
            final_suppliers_list_countwise = list(itertools.chain.from_iterable([i['countwise'] for i in suppliers_dict.values()]))
            final_suppliers_list_amountwise = list(itertools.chain.from_iterable([i['amountwise'] for i in suppliers_dict.values()]))
        if product:
            by_value_supplier_product = Tender.objects.filter(goods_services__goods_services_category__id=product,supplier__supplier_id__in=final_suppliers_list_amountwise,supplier__isnull=False,goods_services__goods_services_category__isnull=False).values('supplier__id','supplier__supplier_name','goods_services__goods_services_category__id','goods_services__goods_services_category__category_name').annotate(local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd'),count=Count('id'))
            by_value_product_country = Tender.objects.filter(goods_services__goods_services_category__id=product,supplier__supplier_id__in=final_suppliers_list_amountwise,supplier__isnull=False,goods_services__goods_services_category__isnull=False).values('goods_services__goods_services_category__id','goods_services__goods_services_category__category_name','country__id','country__name').annotate(local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd'),count=Count('id'))
            by_number_supplier_product = Tender.objects.filter(goods_services__goods_services_category__id=product,supplier__supplier_id__in=final_suppliers_list_countwise,supplier__isnull=False,goods_services__goods_services_category__isnull=False).values('supplier__id','supplier__supplier_name','goods_services__goods_services_category__id','goods_services__goods_services_category__category_name').annotate(local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd'),count=Count('id'))
            by_number_product_country = Tender.objects.filter(goods_services__goods_services_category__id=product,supplier__supplier_id__in=final_suppliers_list_countwise,supplier__isnull=False,goods_services__goods_services_category__isnull=False).values('goods_services__goods_services_category__id','goods_services__goods_services_category__category_name','country__id','country__name').annotate(local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd'),count=Count('id'))  
        else:
            by_value_supplier_product = Tender.objects.filter(supplier__supplier_id__in=final_suppliers_list_amountwise,supplier__isnull=False,goods_services__goods_services_category__isnull=False).values('supplier__id','supplier__supplier_name','goods_services__goods_services_category__id','goods_services__goods_services_category__category_name').annotate(local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd'),count=Count('id'))
            by_value_product_country = Tender.objects.filter(supplier__supplier_id__in=final_suppliers_list_amountwise,supplier__isnull=False,goods_services__goods_services_category__isnull=False).values('goods_services__goods_services_category__id','goods_services__goods_services_category__category_name','country__id','country__name').annotate(local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd'),count=Count('id'))
        
            by_number_supplier_product = Tender.objects.filter(supplier__supplier_id__in=final_suppliers_list_countwise,supplier__isnull=False,goods_services__goods_services_category__isnull=False).values('supplier__id','supplier__supplier_name','goods_services__goods_services_category__id','goods_services__goods_services_category__category_name').annotate(local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd'),count=Count('id'))
            by_number_product_country = Tender.objects.filter(supplier__supplier_id__in=final_suppliers_list_countwise,supplier__isnull=False,goods_services__goods_services_category__isnull=False).values('goods_services__goods_services_category__id','goods_services__goods_services_category__category_name','country__id','country__name').annotate(local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd'),count=Count('id'))
        results = {
                    "by_number": {
                        "product_country": [
                        {
                            "amount_local": i['local'],
                            "amount_usd": i['usd'],
                            "country_id": i['country__id'],
                            "country_name": i['country__name'],
                            "product_id": i['goods_services__goods_services_category__id'],
                            "product_name": i['goods_services__goods_services_category__category_name'],
                            "tender_count": i['count']
                        }
                        for i in by_number_product_country
                        ],
                        "supplier_product": [
                        {
                            "amount_local": i['local'],
                            "amount_usd": i['usd'],
                            "product_id": i['goods_services__goods_services_category__id'],
                            "product_name": i['goods_services__goods_services_category__category_name'],
                            "supplier_id": i['supplier__id'],
                            "supplier_name": i['supplier__supplier_name'],
                            "tender_count": i['count']
                        }
                        for i in by_number_supplier_product
                        ]
                    },
                    "by_value": {
                        "product_country": [
                        {
                            "amount_local": i['local'],
                            "amount_usd": i['usd'],
                            "country_id": i['country__id'],
                            "country_name": i['country__name'],
                            "product_id": i['goods_services__goods_services_category__id'],
                            "product_name": i['goods_services__goods_services_category__category_name'],
                            "tender_count": i['count']
                        }
                        for i in by_value_product_country
                        ],
                        "supplier_product": [
                        {
                            "amount_local": i['local'],
                            "amount_usd": i['usd'],
                            "product_id": i['goods_services__goods_services_category__id'],
                            "product_name": i['goods_services__goods_services_category__category_name'],
                            "supplier_id": i['supplier__id'],
                            "supplier_name": i['supplier__supplier_name'],
                            "tender_count": i['count']
                        }
                        for i in by_value_supplier_product
                        ]
                    }
                }    
        return JsonResponse(results)
        
        

class ProductDistributionView(APIView):
    def get(self,request):
        filter_args = {}
        country =  self.request.GET.get('country',None)
        buyer = self.request.GET.get('buyer',None)
        if country: filter_args['country__country_code_alpha_2'] = country
        if buyer:
            if buyer != 'notnull': 
                filter_args['contract__buyer__buyer_id'] = buyer
            else:
                filter_args['contract__buyer__isnull'] = False
        result=[]
        goods_services = GoodsServices.objects.filter(**filter_args).values('goods_services_category__category_name',
                    'goods_services_category__id','country__currency').annotate(tender=Count('goods_services_category'),
                    local=Sum('contract_value_local'),usd=Sum('contract_value_usd'))
        for goods in goods_services:
            data={}
            data['product_name'] = goods['goods_services_category__category_name']
            data['product_id'] = goods['goods_services_category__id']
            if country:
                data['local_currency_code'] = goods['country__currency']
            else:
                data['local_currency_code'] = 'USD'
            data['tender_count'] = goods['tender']
            data['amount_local'] = goods['local']
            data['amount_usd'] = goods['usd']
            result.append(data)
        return JsonResponse(result,safe=False)

            
class EquityIndicatorView(APIView):
    def get(self,request):
        filter_args = {}
        country =  self.request.GET.get('country',None)
        buyer = self.request.GET.get('buyer')
        if country: filter_args['country__country_code_alpha_2'] = country
        if buyer: filter_args = add_filter_args('buyer',buyer,filter_args)
        result=[]
        if country:
            try:
                country_instance = Country.objects.get(country_code_alpha_2=country)
                filter_args['country'] = country_instance
                tenders_assigned = Tender.objects.filter(**filter_args).exclude(equity_category=None).aggregate(total_usd=Sum('goods_services__contract_value_usd'),total_local=Sum('goods_services__contract_value_local'))
                assigned_count = Tender.objects.filter(**filter_args).exclude(equity_category=None).count()
                filter_args['equity_category'] = None
                tenders_unassigned = Tender.objects.filter(**filter_args).aggregate(total_usd=Sum('goods_services__contract_value_usd'),total_local=Sum('goods_services__contract_value_local'))
                unassigned_count = Tender.objects.filter(**filter_args).count()
                data=[{
                    "amount_local": tenders_assigned['total_local'],
                    "amount_usd": tenders_assigned['total_usd'],
                    "tender_count": assigned_count,
                    "local_currency_code": country_instance.currency,
                    "type": "assigned"
                },
                {
                    "amount_local": tenders_unassigned['total_local'],
                    "amount_usd": tenders_unassigned['total_usd'],
                    "tender_count": unassigned_count,
                    "local_currency_code": country_instance.currency ,
                    "type": "unassigned"
                },]
                return JsonResponse(data,safe=False)
            except Exception as DoesNotExist:
                results = [{"error":"Invalid country_code"}]
                return JsonResponse(results,safe=False)
        else:
            tenders_assigned = Tender.objects.filter(**filter_args).exclude(equity_category=None).aggregate(total_usd=Sum('goods_services__contract_value_usd'),total_local=Sum('goods_services__contract_value_local'))
            assigned_count = Tender.objects.filter(**filter_args).exclude(equity_category=None).count()
            filter_args['equity_category'] = None
            tenders_unassigned = Tender.objects.filter(**filter_args).aggregate(total_usd=Sum('goods_services__contract_value_usd'),total_local=Sum('goods_services__contract_value_local'))
            unassigned_count = Tender.objects.filter(**filter_args).count()
            data=[{
                    "amount_local": tenders_assigned['total_local'],
                    "amount_usd": tenders_assigned['total_usd'],
                    "tender_count": assigned_count,
                    "local_currency_code": "USD",
                    "type": "assigned"
                },
                {
                    "amount_local": tenders_unassigned['total_local'],
                    "amount_usd": tenders_unassigned['total_usd'],
                    "tender_count": unassigned_count,
                    "local_currency_code": "USD" ,
                    "type": "unassigned"
                },]  
            return JsonResponse(data,safe=False)


class ProductTimelineView(APIView):
    def get(self,request):
        filter_args = {}
        country =  self.request.GET.get('country',None)
        buyer = self.request.GET.get('buyer')
        if country: filter_args['country__country_code_alpha_2'] = country
        if buyer: filter_args = add_filter_args('buyer',buyer,filter_args)
        result=[]
        if country:
            try:
                country_instance = Country.objects.get(country_code_alpha_2=country)
                currency = country_instance.currency
                filter_args['country'] = country_instance
                tenders_assigned = Tender.objects.filter(**filter_args).exclude(goods_services__goods_services_category=None).annotate(month=TruncMonth('contract_date')).values('month','goods_services__goods_services_category__category_name','goods_services__goods_services_category__id').annotate(count=Count('id'),local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd')).order_by("-month")
                for tender in tenders_assigned:
                    data={}
                    data['amount_local'] = tender['local']
                    data['amount_usd'] = tender['usd']
                    data['date'] = tender['month']
                    data['local_currency_code'] = currency
                    data['product_id'] = tender['goods_services__goods_services_category__id']
                    data['product_name'] = tender['goods_services__goods_services_category__category_name']
                    data['tender_count'] = tender['count']
                    result.append(data)
                return JsonResponse(result,safe=False)
            except Exception as DoesNotExist:
                result = [{"error":"Invalid country_code"}]
                return JsonResponse(result,safe=False)
        else:
            tenders_assigned = Tender.objects.filter(**filter_args).exclude(goods_services__goods_services_category=None).annotate(month=TruncMonth('contract_date')).values('month','goods_services__goods_services_category__category_name','goods_services__goods_services_category__id').annotate(count=Count('id'),local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd')).order_by("-month")
            try:
                for tender in tenders_assigned:
                    data={}
                    data['amount_local'] = tender['local']
                    data['amount_usd'] = tender['usd']
                    data['date'] = tender['month']
                    data['local_currency_code'] = 'USD'
                    data['product_id'] = tender['goods_services__goods_services_category__id']
                    data['product_name'] = tender['goods_services__goods_services_category__category_name']
                    data['tender_count'] = tender['count']
                    result.append(data)
                return JsonResponse(result,safe=False)
            except Exception as DoesNotExist:
                result = [{"error":"Invalid country_code"}]
                return JsonResponse(result,safe=False)
            return JsonResponse(data,safe=False)


class ProductTimelineRaceView(APIView):
    def get(self,request):
        filter_args={}
        country =  self.request.GET.get('country',None)
        buyer = self.request.GET.get('buyer')
        supplier = self.request.GET.get('supplier')
        currency ="USD"
        if supplier: filter_args = add_filter_args('supplier',supplier,filter_args)
        if country: 
            filter_args['country__country_code_alpha_2'] = country
            instance = Country.objects.get(country_code_alpha_2=country)
            currency = instance.currency
        if buyer: filter_args = add_filter_args('buyer',buyer,filter_args)
        cum_dict = {}
        final_data = []
        categories = GoodsServicesCategory.objects.all()
        tenders = Tender.objects.exclude(goods_services__goods_services_category=None).annotate(month=TruncMonth('contract_date')).values('month').annotate(count=Count('id')).order_by("month")
        for tender in tenders:
            end_date = tender['month'] + dateutil.relativedelta.relativedelta(months=-1)
            start_date=tender['month']
            result = {}
            result["month"]=str(start_date.year)+'-'+str(start_date.month)
            result["details"] = []
            for category in categories:
                data={}
                if country:
                    a = GoodsServices.objects.filter(contract__country__country_code_alpha_2=country,goods_services_category=category,contract__contract_date__gte=start_date,contract__contract_date__lte=end_date).values('goods_services_category__category_name','goods_services_category__id').annotate(count=Count('id'),local=Sum('contract_value_local'),usd=Sum('contract_value_usd'))
                else:
                    a = GoodsServices.objects.filter(goods_services_category=category,contract__contract_date__gte=start_date,contract__contract_date__lte=end_date).values('goods_services_category__category_name','goods_services_category__id').annotate(count=Count('id'),local=Sum('contract_value_local'),usd=Sum('contract_value_usd'))
                tender_count = Tender.objects.filter(contract_date__gte=start_date,contract_date__lte=end_date,goods_services__goods_services_category=category).count()
                data["product_name"]=category.category_name
                data["product_id"]=category.id
                local_value = [i['local'] for i in a]
                usd_value = [i['usd'] for i in a]
                if category.category_name in cum_dict.keys():
                    if 'local' in cum_dict[category.category_name].keys():
                        cum_dict[category.category_name]['local'] = cum_dict[category.category_name]['local'] + (local_value[0] if local_value else 0)
                    if 'usd' in cum_dict[category.category_name].keys():
                        cum_dict[category.category_name]['usd'] = cum_dict[category.category_name]['usd'] + (usd_value[0] if usd_value else 0)
                    if 'count' in cum_dict[category.category_name].keys():
                        cum_dict[category.category_name]['count'] = cum_dict[category.category_name]['count'] + tender_count
                else:
                    cum_dict[category.category_name]={'local': 0 ,'usd': 0, 'count':0}
                    print(local_value)
                    cum_dict[category.category_name]['local'] = cum_dict[category.category_name]['local'] + (local_value[0] if local_value else 0)
                    cum_dict[category.category_name]['usd'] = cum_dict[category.category_name]['usd'] + (usd_value[0] if usd_value else 0)
                    cum_dict[category.category_name]['count'] = cum_dict[category.category_name]['count'] + tender_count
                data["amount_local"] = cum_dict[category.category_name]['local']
                data["amount_usd"] = cum_dict[category.category_name]['usd']
                data["currency"] = currency  
                data["tender_count"]= cum_dict[category.category_name]['count']
                result["details"].append(data)
            final_data.append(result)
        return JsonResponse(final_data,safe=False)

        
class SupplierProfileView(APIView):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        data={}
        try:
            instance = Supplier.objects.get(id=pk)
            supplier_detail = Tender.objects.filter(supplier_id=pk).values('country__name','country__country_code_alpha_2').annotate(total_usd=Sum('goods_services__contract_value_usd'),total_local=Sum('goods_services__contract_value_local'))
            tender_count = Tender.objects.filter(supplier_id=pk).count()
            data['name'] = instance.supplier_name
            data['id'] = pk
            data['code'] = instance.supplier_id
            data['address'] = instance.supplier_address
            data['amount_usd'] = supplier_detail[0]['total_usd']
            data['amount_local'] = supplier_detail[0]['total_local']
            data['tender_count'] = tender_count
            data['country_code'] = supplier_detail[0]['country__country_code_alpha_2']
            data['country_name'] = supplier_detail[0]['country__name']
            return JsonResponse(data,safe=False)
        except Exception as e:
            data['error'] = "Enter valid ID"
            return JsonResponse(data,safe=False)


class BuyerProfileView(APIView):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        data={}
        try:
            instance = Buyer.objects.get(id=pk)
            buyer_detail = Tender.objects.filter(buyer_id=pk).values('country__name','country__country_code_alpha_2').annotate(total_usd=Sum('goods_services__contract_value_usd'),total_local=Sum('goods_services__contract_value_local'))
            tender_count = Tender.objects.filter(buyer_id=pk).count()
            data['name'] = instance.buyer_name
            data['id'] = pk
            data['code'] = instance.buyer_id
            data['address'] = instance.buyer_address
            data['amount_usd'] = buyer_detail[0]['total_usd']
            data['amount_local'] = buyer_detail[0]['total_local']
            data['tender_count'] = tender_count
            data['country_code'] = buyer_detail[0]['country__country_code_alpha_2']
            data['country_name'] = buyer_detail[0]['country__name']
            return JsonResponse(data,safe=False)
        except Exception as e:
            data['error'] = "Enter valid ID"
            return JsonResponse(data,safe=False)

class CountryPartnerView(APIView):
    def get(self,request):
        filter_args = {}
        country =  self.request.GET.get('country',None)
        if country: filter_args['country__country_code_alpha_2'] = country
        try:
            country_partner = CountryPartner.objects.filter(**filter_args)
        except Exception as DoesNotExist:
            country_partner = [{"error": "Country partner doesnot exist for this country"}]
        result=[]
        if country_partner:
            for i in country_partner:
                data={}
                data["name"]= i.name
                data["description"]= i.description
                data["email"]= i.email
                data["website"]= i.website
                data["logo"]= json.dumps(str(i.logo))
                data["order"]= i.order
                data["country"]= json.dumps(str(i.country))
                result.append(data)
        else:
            result ={
                "error": "Country Partner not found for this country"
            }
        return JsonResponse(result,safe=False)


class BuyerSummaryView(APIView):
    def get(self,request):
        filter_args = {}
        country =  self.request.GET.get('country',None)
        result = {}
        trend = []
        current_time = datetime.datetime.now()
        previous_month_date = current_time - dateutil.relativedelta.relativedelta(months=-1)
        previous_month = previous_month_date.replace(day=1).date()
        if country: filter_args['country__country_code_alpha_2'] = country
        buyer_details = Tender.objects.filter(**filter_args).exclude(buyer__isnull=True).annotate(month=TruncMonth('contract_date')).values('month').annotate(count=Count('buyer_id',distinct=True)).order_by("-month")
        totals = Tender.objects.filter(**filter_args).exclude(buyer__isnull=True).values('buyer').distinct().aggregate(total=Count('buyer'))
        for details in buyer_details:
            data = {}
            data['buyer_count'] = details['count']
            data['month'] = details['month']
            trend.append(data)
        try:
            dates_in_details = [i['month'] for i in buyer_details]
            final_current_month_count = [buyer_details[0]['count'] if current_time.replace(day=1).date() in dates_in_details else 0]
            final_previous_month_count = [buyer_details[1]['count'] if previous_month in dates_in_details else 0]
            percentage = round((( final_current_month_count[0] - final_previous_month_count[0])/final_previous_month_count[0])*100)
            print(final_current_month_count)
            print(final_previous_month_count)
        except:
            percentage = 0
        result['total'] = totals['total']
        result['percentage'] = percentage
        result['trend'] = trend
        return JsonResponse(result,safe=False)


class SupplierSummaryView(APIView):
    def get(self,request):
        filter_args = {}
        country =  self.request.GET.get('country',None)
        result = {}
        trend = []
        current_time = datetime.datetime.now()
        previous_month_date = current_time - dateutil.relativedelta.relativedelta(months=-1)
        previous_month = previous_month_date.replace(day=1).date()
        if country: filter_args['country__country_code_alpha_2'] = country
        supplier_details = Tender.objects.filter(**filter_args).exclude(supplier__isnull=True).annotate(month=TruncMonth('contract_date')).values('month').annotate(count=Count('supplier_id',distinct=True)).order_by("-month")
        totals = Tender.objects.filter(**filter_args).exclude(supplier__isnull=True).values('supplier').distinct().aggregate(total=Count('supplier'))
        for details in supplier_details:
            data = {}
            data['supplier_count'] = details['count']
            data['month'] = details['month']
            trend.append(data)
        try:
            dates_in_details = [i['month'] for i in supplier_details]
            final_current_month_count = [supplier_details[0]['count'] if current_time.replace(day=1).date() in dates_in_details else 0]
            final_previous_month_count = [supplier_details[1]['count'] if previous_month in dates_in_details else 0]
            percentage = round((( final_current_month_count[0] - final_previous_month_count[0])/final_previous_month_count[0])*100)
        except:
            percentage = 0
        result['total'] = totals['total']
        result['percentage'] = percentage
        result['trend'] = trend
        return JsonResponse(result,safe=False)


class ProductSummaryView(APIView):
    def get(self,request):
        filter_args = {}
        country =  self.request.GET.get('country',None)
        currency= 'USD'
        if country: 
            filter_args['country__country_code_alpha_2'] = country
            instance = Country.objects.get(country_code_alpha_2=country)
            currency = instance.currency
        result = []
        tenders_assigned = Tender.objects.filter(**filter_args).exclude(goods_services__goods_services_category=None).annotate(category=Count('goods_services__goods_services_category__category_name')).values('goods_services__goods_services_category__category_name','goods_services__goods_services_category__id').annotate(count=Count('id'),local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd'))
        for tender in tenders_assigned:
            data={}
            data['amount_local'] = tender['local']
            data['amount_usd'] = tender['usd']
            data['local_currency_code'] = currency 
            data['product_id'] = tender['goods_services__goods_services_category__id']
            data['product_name'] = tender['goods_services__goods_services_category__category_name']
            data['tender_count'] = tender['count']
            result.append(data)
        return JsonResponse(result,safe=False)

class FilterParams(APIView):
    def get(self, request, *args, **kwargs):
        try:
            buyers = Buyer.objects.values('id','buyer_name')
            suppliers = Supplier.objects.values('id','supplier_name')
            countries = Country.objects.values('id','country_code','name')
            products = GoodsServicesCategory.objects.values('id','category_name')

            result_buyer=[]
            result_supplier=[]
            result_country =[]
            result_product =[]
            result={}

            if buyers:
                result_buyer = [
                    {
                        'id' : buyer['id'],
                        'name': buyer['buyer_name']
                    }
                    for buyer in buyers
                    ]
            if suppliers:
                result_supplier = [
                   {
                        'id' : supplier['id'],
                        'name': supplier['supplier_name']
                    }
                    for supplier in suppliers 
                ]
                    
            if countries:
                result_country = [
                   {
                        'id' : country['id'],
                        'code': country['country_code'],
                        'name' : country['name']
                    }
                    for country in countries 
                ]
              
            if products:
                result_product = [
                   {
                        'id' : product['id'],
                        'name': product['category_name']
                    }
                    for product in products
                ]
            
            result = {
                "buyer": result_buyer,
                "contracts": {
                "method": [
                {
                    "label": "Direct",
                    "value": "direct"
                },
                {
                    "label": "Limited",
                    "value": "limited"
                },
                {
                    "label": "Open",
                    "value": "open"
                },
                {
                    "label": "Other",
                    "value": "other"
                },
                {
                    "label": "Selective",
                    "value": "selective"
                }
                ],
                "status": [
                {
                    "label": "Active",
                    "value": "active"
                },
                {
                    "label": "Cancelled",
                    "value": "cancelled"
                },
                {
                    "label": "Completed",
                    "value": "completed"
                },
                {
                    "label": "Other",
                    "value": "other"
                }
                ]
            },
            "country": result_country,
            "product": result_product,
            "supplier": result_supplier
            }
            
            return JsonResponse(result,safe=False)

        except Exception as DoesNotExist:
            result = [{"error": "No buyer and supplier data available"}]
            return JsonResponse(result,safe=False)


class EquitySummaryView(APIView):
    def get(self,request):
        filter_args={}
        country =  self.request.GET.get('country',None)
        if country: filter_args['country__country_code_alpha_2'] = country
        filter_args['equity_category__isnull']=False
        result=[]
        equity_summary = Tender.objects.filter(**filter_args).annotate(month=TruncMonth('contract_date')).values('month','equity_category','equity_category__category_name').annotate(total=Count('id'),local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd')).order_by("-month")
        for detail in equity_summary:
            data={}
            data['amount_local'] = detail['local']
            data['amount_usd'] = detail['usd']
            data['equity'] = detail['equity_category__category_name']
            data['equity_category_id'] = detail['equity_category']
            data['month'] = detail['month']
            data['tender_count'] = detail['total']
            result.append(data)
        return JsonResponse(result,safe=False)


class ProductTableView(APIView):
    def get(self,request):
        filter_args={}
        country =  self.request.GET.get('country',None)
        if country: filter_args['country__country_code_alpha_2'] = country
        filter_args['goods_services__goods_services_category__isnull'] = False 
        result=[]
        product_tables =  Tender.objects.filter(**filter_args).values('goods_services__goods_services_category__category_name','goods_services__goods_services_category__id').annotate(total=Count('id'),local=Sum('goods_services__contract_value_local'),usd=Sum('goods_services__contract_value_usd'),buyer=Sum('buyer'),supplier=Sum('supplier'))
        for product in product_tables:
            data={}
            data['amount_local'] = product['local']
            data['amount_usd'] = product['usd']
            data['product_id'] = product['goods_services__goods_services_category__id']
            data['product_name'] = product['goods_services__goods_services_category__category_name']
            data['buyer_count'] = product['buyer']
            data['supplier_count'] = product['supplier']
            data['tender_count'] = product['total']
            result.append(data)
        return JsonResponse(result,safe=False)


class FilterParametersSuppliers(APIView):
    def get(self,request):
        filter_args={}
        result=[]
        country =  self.request.GET.get('country',None)
        try:
            if country: 
                filter_args['country__country_code_alpha_2'] = country
                instance = Country.objects.get(country_code_alpha_2=country)
                country_code = instance.country_code_alpha_2
            filter_args['supplier__isnull']=False
            suppliers = Tender.objects.filter(**filter_args).values('supplier__id','supplier__supplier_name').distinct()
            for supplier in suppliers:
                data={}
                data['id'] = supplier['supplier__id']
                data['name'] =  supplier['supplier__supplier_name']
                if country:
                    data['country_code'] = country_code
                else:
                    data['country_code'] = "USD"
                result.append(data)
            return JsonResponse(result,safe=False)
        except Exception as DoesNotExist:
            result = [{"error": "Country code doest not exists"}]
            return JsonResponse(result,safe=False)

class FilterParametersBuyers(APIView):
    def get(self,request):
        filter_args={}
        result=[]
        country =  self.request.GET.get('country',None)
        try:
            if country: 
                filter_args['country__country_code_alpha_2'] = country
                instance = Country.objects.get(country_code_alpha_2=country)
                country_code = instance.country_code_alpha_2
            filter_args['buyer__isnull']=False
            buyers = Tender.objects.filter(**filter_args).values('buyer__id','buyer__buyer_name').distinct()
            for buyer in buyers:
                data={}
                data['id'] = buyer['buyer__id']
                data['name'] =  buyer['buyer__buyer_name']
                if country:
                    data['country_code'] = country_code
                else:
                    data['country_code'] = "USD"
                result.append(data)
            return JsonResponse(result,safe=False)
        except Exception as DoesNotExist:
            result = [{"error": "Country code doest not exists"}]
            return JsonResponse(result,safe=False)

class FilterParametersStatic(APIView):
    def get(self,request):
        filter_args={}
        countries = Country.objects.values('id','country_code','name')
        products = GoodsServicesCategory.objects.values('id','category_name')
        equities = EquityCategory.objects.values('id','category_name')
        result_country =[]
        result_product =[]
        result_equity = []
        result={}
        if countries:
            result_country = [
                {
                    'id' : country['id'],
                    'code': country['country_code'],
                    'name' : country['name']
                }
                for country in countries 
            ]
              
        if products:
            result_product = [
            {
                    'id' : product['id'],
                    'name': product['category_name']
                }
                for product in products
            ]

        if equities:
            result_equity = [
            {
                    'id' : equity['id'],
                    'name': equity['category_name']
                }
                for equity in equities
            ]
        result['method'] = [
                {
                    "label": "Direct",
                    "value": "direct"
                },
                {
                    "label": "Limited",
                    "value": "limited"
                },
                {
                    "label": "Open",
                    "value": "open"
                },
                {
                    "label": "Other",
                    "value": "other"
                },
                {
                    "label": "Selective",
                    "value": "selective"
                }
                ]
        result["status"]= [
                {
                    "label": "Active",
                    "value": "active"
                },
                {
                    "label": "Cancelled",
                    "value": "cancelled"
                },
                {
                    "label": "Completed",
                    "value": "completed"
                },
                {
                    "label": "Other",
                    "value": "other"
                }
                ]
        result['country'] = result_country
        result['products'] = result_product
        return JsonResponse(result,safe=False)


class ProductSpendingComparision(APIView):
    def get(self,request):
        amount_usd_local =  Tender.objects.annotate(month=TruncMonth('contract_date')).values('country__country_code','country__currency','month','goods_services__goods_services_category__id','goods_services__goods_services_category__category_name').annotate(usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_usd')).order_by('-month')
        count =  Tender.objects.annotate(month=TruncMonth('contract_date')).values('country__country_code','country__currency','month','goods_services__goods_services_category__id','goods_services__goods_services_category__category_name').annotate(count=Count('id')).order_by('-month')
        # import ipdb; ipdb.set_trace()
        result = [
            {
                "amount_local": i['local'],
                "amount_usd": i['usd'],
                "country_code": i['country__country_code'],
                "currency": i['country__currency'],
                "month": i['month'],
                "product_id": i['goods_services__goods_services_category__id'],
                "product_name": i['goods_services__goods_services_category__category_name']
            }
            for i in amount_usd_local
        ] 
        for i in range(len(count)):
            result[i]['tender_count'] = count[i]['count']
        return JsonResponse(result,safe=False)