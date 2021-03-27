import gspread
from django.conf import settings
from django.core.management.base import BaseCommand

from country.models import Country
from country.tasks import import_tender_data


class Command(BaseCommand):
    help = "Import tender from google sheets url"

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, help="Public access google sheet url")

    def handle(self, *args, **kwargs):
        gs_sheet_url = kwargs["url"]
        print(f"Fetching tender data from {gs_sheet_url}")

        gc = gspread.service_account(filename=settings.GOOGLE_SHEET_CREDENTIALS_JSON)
        covid_sheets = gc.open_by_url(gs_sheet_url)

        try:
            worksheet_settings = covid_sheets.worksheet("settings")

            # Get country and currency from worksheet:settings
            country = worksheet_settings.cell(2, 3).value

            # Check if country exists in our database
            result = Country.objects.filter(name=country).first()
            if not result:
                print(f'Country "{country}" does not exists in our database.')
            else:
                import_tender_data.apply_async(args=(gs_sheet_url,), queue="covid19")
                print("Created task: import_tender_data")
        except Exception as e:
            print(e)
