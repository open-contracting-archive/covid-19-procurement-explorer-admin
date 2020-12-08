from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.views import APIView
from .serializers import TenderSerializer
from country.models import Tender

import datetime 
import dateutil.relativedelta
from django.db.models import Count,Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse

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
            this_month = Tender.objects.filter(contract_date__year=today.year,
                            contract_date__month=today.month).aggregate(Sum('contract_value_usd'))
            earlier_month = Tender.objects.filter(contract_date__year=earlier.year,
                            contract_date__month=earlier.month).aggregate(Sum('contract_value_usd'))
            try:
                increment = ((this_month['contract_value_usd__sum'] - earlier_month['contract_value_usd__sum'])/earlier_month['contract_value_usd__sum'])*100
            
            except Exception:
                increment =0
            except ZeroDivisionError:
                increment = 0
            bar_chart = Tender.objects.values('procurement_procedure').annotate(sum=Sum('contract_value_usd'))

            for i in bar_chart:
                if i['procurement_procedure']=='selective':
                    selective_sum = i['sum']
                elif i['procurement_procedure']=='limited':
                    limited_sum = i['sum']
                elif i['procurement_procedure']=='open':
                    open_sum = i['sum']
                elif i['procurement_procedure']=='direct':
                    direct_sum = i['sum']
            line_chart = Tender.objects.annotate(month=TruncMonth('contract_date')).values('month').annotate(total=Sum('contract_value_usd')).order_by("-month")
            line_chart_list = []
            for i in line_chart:
                a= {}
                a['date']= i['month']
                a['value'] = i['total']
                line_chart_list.append(a)
            result = {
                'usd':{'total':total_tender_amount['contract_value_usd__sum'],
                        'increment':increment,
                        "line_chart" : line_chart_list,
                        'bar_chart':{
                            'open':open_sum,
                            'limited':limited_sum,
                            'selective':selective_sum,
                            'direct':direct_sum,
                            }
                        }
            }
        else:
            total_country_tender_amount = Tender.objects.filter(country__name=country).aggregate(Sum('contract_value_usd'))
            this_month = Tender.objects.filter(country__name=country,contract_date__year=today.year,
                            contract_date__month=today.month).aggregate(Sum('contract_value_usd'))
            earlier_month = Tender.objects.filter(country__name=country,contract_date__year=earlier.year,
                            contract_date__month=earlier.month).aggregate(Sum('contract_value_usd'))
            try:
                increment = ((this_month['contract_value_usd__sum'] - earlier_month['contract_value_usd__sum'])/earlier_month['contract_value_usd__sum'])*100
            
            except Exception:
                increment =0
                
            except ZeroDivisionError:
                increment = 0
            bar_chart =Tender.objects.filter(country__name=country).values('procurement_procedure').annotate(sum=Sum('contract_value_usd'))
            for i in bar_chart:
                if i['procurement_procedure']=='selective':
                    selective_total = i['sum']
                elif i['procurement_procedure']=='limited':
                    limited_total = i['sum']
                elif i['procurement_procedure']=='open':
                    open_total = i['sum']
                elif i['procurement_procedure']=='direct':
                    direct_total = i['sum']
            line_chart = Tender.objects.filter(country__name=country).annotate(month=TruncMonth('contract_date')).values('month').annotate(total=Sum('contract_value_usd')).order_by("-month")
            line_chart_list = []
            for i in line_chart:
                a= {}
                a['date']= i['month']
                a['value'] = i['total']
                line_chart_list.append(a)
            result = {'usd':{'total':total_country_tender_amount['contract_value_usd__sum'],
                        'increment':increment,
                        "line_chart" : line_chart_list,
                        'bar_chart':{
                            'open':open_total,
                            'limited':limited_total,
                            'selective':selective_total,
                            'direct':direct_total,}
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
                        'bar_chart':{
                            'open':open_count,
                            'limited':limited_count,
                            'selective':selective_count,
                            'direct':direct_count,}
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
                        'bar_chart':{
                            'open':open_count,
                            'limited':limited_count,
                            'selective':selective_count,
                            'direct':direct_count,}
                        }
        return JsonResponse(result)