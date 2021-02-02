from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import gspread

from country.models import Country
from country.tasks import import_tender_data, import_tender_data_excel
import pandas as pd


class Command(BaseCommand):
    help = 'Import tender from excel file'

    def add_arguments(self, parser):
        parser.add_argument('country', type=str, help='Country to import tender')
        parser.add_argument('file', type=str, help='Excel file path')

    def handle(self, *args, **kwargs):
        country = kwargs['country']
        excel_file_path = kwargs['file']
        print(f'Fetching tender data from {excel_file_path} for country {country}')

        try:
            # ws = pd.read_excel(excel_file_path, sheet_name=['data'], header=None)
            # ws_settings = ws['settings']
            # '/Users/bigyan/UKRAINIAN DATA COVID_11.12.20.xlsx'
            # Check if country exists in our database
            result = Country.objects.filter(name=country).first()
            country = result.name
            currency = result.currency

            
            if not result:
                print(f'Country "{country}" does not exists in our database.')
            else:
                r = import_tender_data_excel.apply_async(args=(excel_file_path,country,currency), queue='covid19')
                print('Created task: import_tender_data')
        except Exception as e:
            print(e)