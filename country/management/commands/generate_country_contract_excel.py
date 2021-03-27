from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from country.models import Country, Tender, Buyer, Supplier
from django.db.models import Avg, Count, Min, Sum, Count,Window,Q
import xlsxwriter 
import os
from pathlib import Path
from country.tasks import country_contract_excel

class Command(BaseCommand):
    help = 'Generate Country Contract Excel !!'

    def add_arguments(self, parser):
        parser.add_argument('--country', type=str)

    def handle(self, *args, **kwargs):
        country = kwargs['country']
        country_contract_excel.apply_async(args=(country,), queue='covid19')