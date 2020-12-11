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

from country.models import Tender,Country,CovidMonthlyActiveCases


class TotalSpendingsView(APIView):
    def get(self,request):
        """
        Return a list of all contracts.
        """
        #Calculating total tender
        country =  self.request.GET.get('country',None)
        today = datetime.datetime.now()
        one_month_earlier = today + dateutil.relativedelta.relativedelta(months=-1)
        earlier = one_month_earlier.replace(day=1).date()

        if country == None:
            total_tender_amount = Tender.objects.aggregate(Sum('contract_value_usd'))
            total_tender_local_amount = Tender.objects.aggregate(Sum('contract_value_local'))
            this_month = Tender.objects.filter(contract_date__year=today.year,
                            contract_date__month=today.month).aggregate(Sum('contract_value_usd'))
            this_month_local = Tender.objects.filter(contract_date__year=today.year,
                            contract_date__month=today.month).aggregate(Sum('contract_value_local'))
            earlier_month = Tender.objects.filter(contract_date__year=earlier.year,
                            contract_date__month=earlier.month).aggregate(Sum('contract_value_usd'))
            earlier_month_local = Tender.objects.filter(contract_date__year=earlier.year,
                            contract_date__month=earlier.month).aggregate(Sum('contract_value_local'))
                

            try:
                increment = ((this_month['contract_value_usd__sum'] - earlier_month['contract_value_usd__sum'])/earlier_month['contract_value_usd__sum'])*100
                increment_local = ((this_month_local['contract_value_local__sum'] - earlier_month_local['contract_value_local__sum'])/earlier_month_local['contract_value_usd__sum'])*100
            except Exception:
                increment =0
                increment_local =0
            except ZeroDivisionError:
                increment = 0
                increment_local = 0
            bar_chart = Tender.objects.values('procurement_procedure').annotate(sum=Sum('contract_value_usd'))
            bar_chart_local = Tender.objects.values('procurement_procedure').annotate(sum=Sum('contract_value_local'))
            selective_sum=0
            limited_sum=0
            open_sum=0
            directsuml=0
            selective_sum_local=0
            limited_sum_local=0
            open_sum_local=0
            direct_sum_local=0
            for i in bar_chart:
                if i['procurement_procedure']=='selective':
                    selective_sum = i['sum']
                elif i['procurement_procedure']=='limited':
                    limited_sum = i['sum']
                elif i['procurement_procedure']=='open':
                    open_sum = i['sum']
                elif i['procurement_procedure']=='direct':
                    direct_sum = i['sum']
            for i in bar_chart_local:
                if i['procurement_procedure']=='selective':
                    selective_sum_local = i['sum']
                elif i['procurement_procedure']=='limited':
                    limited_sum_local = i['sum']
                elif i['procurement_procedure']=='open':
                    open_sum_local = i['sum']
                elif i['procurement_procedure']=='direct':
                    direct_sum_local = i['sum']
            line_chart = Tender.objects.annotate(month=TruncMonth('contract_date')).values('month').annotate(total=Sum('contract_value_usd')).order_by("-month")
            line_chart_local = Tender.objects.annotate(month=TruncMonth('contract_date')).values('month').annotate(total=Sum('contract_value_local')).order_by("-month")
            line_chart_list = []
            line_chart_local_list = []
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
            result = {
                'usd':{'total':total_tender_amount['contract_value_usd__sum'],
                        'increment':increment,
                        "line_chart" : line_chart_list,
                        'bar_chart':[{
                                "method":"open",
                                "value":open_sum
                                },
                            {
                                "method":"limited",
                                "value":limited_sum
                                },
                            {
                                "method":"selective",
                                "value":selective_sum
                                },
                            {
                                "method":"direct",
                                "value":direct_sum
                            }]
                        },
                'local':{
                    'total':total_tender_local_amount['contract_value_local__sum'],
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
        else:
            total_country_tender_amount = Tender.objects.filter(country__name=country).aggregate(Sum('contract_value_usd'))
            total__country_tender_local_amount = Tender.objects.filter(country__name=country).aggregate(Sum('contract_value_local'))
            this_month = Tender.objects.filter(country__name=country,contract_date__year=today.year,
                            contract_date__month=today.month).aggregate(Sum('contract_value_usd'))
            this_month_local = Tender.objects.filter(country__name=country,contract_date__year=today.year,
                            contract_date__month=today.month).aggregate(Sum('contract_value_local'))
            earlier_month = Tender.objects.filter(country__name=country,contract_date__year=earlier.year,
                            contract_date__month=earlier.month).aggregate(Sum('contract_value_usd'))
            earlier_month_local = Tender.objects.filter(country__name=country,contract_date__year=earlier.year,
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
            bar_chart =Tender.objects.filter(country__name=country).values('procurement_procedure').annotate(sum=Sum('contract_value_usd'))
            bar_chart_local = Tender.objects.filter(country__name=country).values('procurement_procedure').annotate(sum=Sum('contract_value_local'))
            selective_total=0
            limited_total=0
            open_total=0
            direct_total=0
            selective_total_local=0
            limited_total_local=0
            open_total_local=0
            direct_total_local=0
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
            line_chart = Tender.objects.filter(country__name=country).annotate(month=TruncMonth('contract_date')).values('month').annotate(total=Sum('contract_value_usd')).order_by("-month")
            line_chart_local = Tender.objects.filter(country__name=country).annotate(month=TruncMonth('contract_date')).values('month').annotate(total=Sum('contract_value_local')).order_by("-month")

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
            result = {'usd':{'total':total_country_tender_amount['contract_value_usd__sum'],
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
                    'total':total__country_tender_local_amount['contract_value_local__sum'],
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
        #Calculating total tender
        country =  self.request.GET.get('country',None)
        today = datetime.datetime.now()
        one_month_earlier = today + dateutil.relativedelta.relativedelta(months=-1)
        earlier = one_month_earlier.replace(day=1).date()
        open_count = 0
        selective_count = 0
        direct_count =0
        limited_count=0
        if country == None:
            total_tender = Tender.objects.all().count()
            this_month = Tender.objects.filter(contract_date__year=today.year,
                            contract_date__month=today.month).count()
            earlier_month = Tender.objects.filter(contract_date__year=earlier.year,
                            contract_date__month=earlier.month).count()
            try:
                difference = ((this_month-earlier_month)/earlier_month)*100
            except ZeroDivisionError:
                difference = 0
            bar_chart = Tender.objects.values('procurement_procedure').annotate(count=Count('procurement_procedure'))
            for i in bar_chart:
                if i['procurement_procedure']=='selective':
                    selective_count = i['count']
                elif i['procurement_procedure']=='limited':
                    limited_count = i['count']
                elif i['procurement_procedure']=='open':
                    open_count = i['count']
                elif i['procurement_procedure']=='direct':
                    direct_count = i['count']
            line_chart = Tender.objects.annotate(month=TruncMonth('contract_date')).values('month').annotate(total=Count('id')).order_by("-month")
            line_chart_list = []
            for i in line_chart:
                a= {}
                a['date']= i['month']
                a['value'] = i['total']
                line_chart_list.append(a)
            result = {'total':total_tender,
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
        else:
            total_country_tender = Tender.objects.filter(country__name=country).count()
            this_month = Tender.objects.filter(country__name=country,contract_date__year=today.year,
                            contract_date__month=today.month).count()
            earlier_month = Tender.objects.filter(country__name=country,contract_date__year=earlier.year,
                            contract_date__month=earlier.month).count()
            try:
                difference = ((this_month-earlier_month)/earlier_month)*100
            except ZeroDivisionError:
                difference = 0
            bar_chart =Tender.objects.filter(country__name=country).values('procurement_procedure').annotate(count=Count('procurement_procedure'))
            for i in bar_chart:
                if i['procurement_procedure']=='selective':
                    selective_count = i['count']
                elif i['procurement_procedure']=='limited':
                    limited_count = i['count']
                elif i['procurement_procedure']=='open':
                    open_count = i['count']
                elif i['procurement_procedure']=='direct':
                    direct_count = i['count']
            line_chart = Tender.objects.filter(country__name=country).annotate(month=TruncMonth('contract_date')).values('month').annotate(total=Count('id')).order_by("-month")
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
        current_time = datetime.datetime.now()
        previous_month_date = current_time - dateutil.relativedelta.relativedelta(months=1)
        previous_month = previous_month_date.replace(day=1).date()

        # Difference percentage calculation 
        filter_args = {}
        if country: filter_args['country__name'] = country
        current_month_sum = Tender.objects.filter(**filter_args,contract_date__year=current_time.year,contract_date__month=current_time.month).aggregate(sum=Sum('goods_services__no_of_bidders'),count=Count('id'))
        previous_month_sum = Tender.objects.filter(**filter_args,contract_date__year=previous_month.year,contract_date__month=previous_month.month).aggregate(sum=Sum('goods_services__no_of_bidders'),count=Count('id'))
        try:
            final_current_month_avg = current_month_sum['sum']/current_month_sum['count'] if current_month_sum['sum'] else 0
            final_previous_month_avg = previous_month_sum['sum']/previous_month_sum['count'] if previous_month_sum['sum'] else 0
            difference = round((( final_current_month_avg - final_previous_month_avg)/final_previous_month_avg)*100)
        except:
            difference = 0
        
        # Month wise average of number of bids for contracts
        monthwise_data = Tender.objects.filter(**filter_args).annotate(month=TruncMonth('contract_date')).values('month').annotate(sum=Sum("goods_services__no_of_bidders"),count=Count('id')).order_by("-month")
        final_line_chart_data = [{'date': i['month'],'value': round(i['sum']/i['count']) if i['sum'] else 0} for i in monthwise_data]
        
        # Overall average number of bids for contracts
        overall_avg = Tender.objects.filter(**filter_args).aggregate(sum=Sum('goods_services__no_of_bidders'),count=Count('id'))

        result ={
            'average' : round(overall_avg['sum']/overall_avg['count']) if overall_avg['sum'] else 0,
            'difference' : difference,
            'line_chart' : final_line_chart_data
        }
        return JsonResponse(result)
        

class GlobalOverView(APIView):
    def get(self,request):
        temp={}
        tender_temp ={}
        data=[]
        count = Tender.objects.annotate(month=TruncMonth('contract_date')).values('month').annotate(total_contract=Count('id'),total_amount=Sum('contract_value_usd')).order_by("month")
        countries = Country.objects.all()
        for i in count:
            result={}
            end_date = i['month'] + dateutil.relativedelta.relativedelta(months=1)
            start_date=i['month']
            result["details"]=[]
            result["month"]=str(start_date.year)+'-'+str(start_date.month)
            for j in countries:
                b={}
                tender_count =Tender.objects.filter(country__name=j,contract_date__gte=start_date,contract_date__lte=end_date).count()
                tender =  Tender.objects.filter(country__name=j,contract_date__gte=start_date,contract_date__lte=end_date).aggregate(Sum('contract_value_usd'))
                b['country']=j.name
                b['country_code']=j.country_code
                b['aplha2_code'] = j.country_code_alpha_2
                if tender['contract_value_usd__sum']==None:
                    tender_val = 0
                else:
                    tender_val = tender['contract_value_usd__sum']
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
        if country:
            for_value = Tender.objects.filter(country__name=country).values('supplier__supplier_id','supplier__supplier_name','country__currency')\
                        .annotate(count=Count('id'),usd=Sum('contract_value_usd'),local=Sum('contract_value_local')).order_by('-usd')[:10]
            for_number = Tender.objects.filter(country__name=country).values('supplier__supplier_id','supplier__supplier_name','country__currency')\
                        .annotate(count=Count('id'),usd=Sum('contract_value_usd'),local=Sum('contract_value_local')).order_by('-count')[:10]
        else:
            for_value = Tender.objects.values('supplier__supplier_id','supplier__supplier_name','country__currency')\
                .annotate(count=Count('id'),usd=Sum('contract_value_usd'),local=Sum('contract_value_local')).order_by('-usd')[:10]
            for_number = Tender.objects.values('supplier__supplier_id','supplier__supplier_name','country__currency')\
                .annotate(count=Count('id'),usd=Sum('contract_value_usd'),local=Sum('contract_value_local')).order_by('-count')[:10]
        by_number= []
        by_value = []
        for value in for_value:
            a= {}
            a["amount_local"] = value['local']
            a["amount_usd"] = value['usd']
            a["local_currency_code"] = value['country__currency']
            a['supplier_id'] = value['supplier__supplier_id']
            a['supplier_name'] = value['supplier__supplier_name']
            a['tender_count'] = value['count']
            by_value.append(a)
        for value in for_number:
            a= {}
            a["amount_local"] = value['local']
            a["amount_usd"] = value['usd']
            a["local_currency_code"] = value['country__currency']
            a['supplier_id'] = value['supplier__supplier_id']
            a['supplier_name'] = value['supplier__supplier_name']
            a['tender_count'] = value['count']
            by_number.append(a)
        result={"by_number": by_number,
                "by_value": by_value}
        return JsonResponse(result)


class TopBuyers(APIView):
    def get(self,request):
        country =  self.request.GET.get('country',None)
        if country:
            for_value = Tender.objects.filter(country__name=country,buyer__isnull=False).values('buyer__buyer_id','buyer__buyer_name','country__currency')\
                        .annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('contract_value_local')).order_by('-usd')[:10]
            for_number = Tender.objects.filter(country__name=country,buyer__isnull=False).values('buyer__buyer_id','buyer__buyer_name','country__currency')\
                        .annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('contract_value_local')).order_by('-count')[:10]
        else:
            for_value = Tender.objects.filter(buyer__isnull=False).values('buyer__buyer_id','buyer__buyer_name','country__currency')\
                .annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('contract_value_local')).order_by('-usd')[:10]
            for_number = Tender.objects.filter(buyer__isnull=False).values('buyer__buyer_id','buyer__buyer_name','country__currency')\
                .annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('contract_value_local')).order_by('-count')[:10]
        by_number= []
        by_value = []
        for value in for_value:
            a= {}
            a["amount_local"] = value['local']
            a["amount_usd"] = value['usd']
            a["local_currency_code"] = value['country__currency']
            a['buyer_id'] = value['buyer__buyer_id']
            a['buyer_name'] = value['buyer__buyer_name']
            a['tender_count'] = value['count']
            by_value.append(a)
        for value in for_number:
            a= {}
            a["amount_local"] = value['local']
            a["amount_usd"] = value['usd']
            a["local_currency_code"] = value['country__currency']
            a['buyer_id'] = value['buyer__buyer_id']
            a['buyer_name'] = value['buyer__buyer_name']
            a['tender_count'] = value['count']
            by_number.append(a)
        result={"by_number": by_number,
                "by_value": by_value}
        return JsonResponse(result)


class DirectOpen(APIView):
    def get(self,request):
        country =  self.request.GET.get('country',None)
        if country:
            amount_direct = Tender.objects.filter(country__name=country, procurement_procedure='direct').values('country__currency').annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local'))
            amount_open = Tender.objects.filter(country__name=country, procurement_procedure='open').values('country__currency').annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local'))
        else:
            amount_direct = Tender.objects.filter( procurement_procedure='direct').values('procurement_procedure').annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local'))
            amount_open = Tender.objects.filter( procurement_procedure='open').values('procurement_procedure').annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local'))

        for i in amount_direct:
            result_direct ={ "amount_local" : i['local'],
                "amount_usd": i['usd'],
                "tender_count": i['count'],
                "local_currency_code":i['country__currency'] if 'country__currency' in i else [],
                "procedure": "direct"
                }

        for i in amount_open:
            result_open ={ "amount_local" : i['local'],
                "amount_usd": i['usd'],
                "tender_count": i['count'],
                "local_currency_code":i['country__currency'] if 'country__currency' in i else [],
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
        if country: filter_args['country__name'] = country

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
            contracts_quantity = Tender.objects.filter(country__name=country).annotate(month=TruncMonth('contract_date')).values('month','country__currency').annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local')).order_by('-month')
        else:
            contracts_quantity = Tender.objects.annotate(month=TruncMonth('contract_date')).values('month').annotate(count=Count('id'),usd=Sum('goods_services__contract_value_usd'),local=Sum('goods_services__contract_value_local')).order_by('-month')
        
        contracts_quantity_list = []
        
        for i in contracts_quantity:
            if country:
                active_case = CovidMonthlyActiveCases.objects.filter(country__name = country, covid_data_date__year=i['month'].year, covid_data_date__month=i['month'].month).values('active_cases_count')
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
            a["amount_local"] = i['local']
            a["amount_usd"] = i['usd']
            a["local_currency_code"] = i['country__currency'] if 'country__currency' in i else ''
            a["month"] = i['month']
            a["tender_count"] = i['count']
            contracts_quantity_list.append(a)

        return JsonResponse(contracts_quantity_list, safe= False) 
