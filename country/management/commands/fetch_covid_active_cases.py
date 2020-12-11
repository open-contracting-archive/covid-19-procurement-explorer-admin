from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from country.models import Country, CovidMonthlyActiveCases
import calendar
import requests


class Command(BaseCommand):
    help = 'Import historical covid active cases data from covid-api.com'

    def handle(self, *args, **kwargs):
        countries = Country.objects.all()
        YEARS = [2020]

        for country in countries:
            country_code = country.country_code

            for year in YEARS:
                for month in range(1,12+1):
                    month_end_day = calendar.monthrange(year, month)[1]
                    date = f'{year}-{month:02}-{month_end_day:02}'

                    existing_db_entry = CovidMonthlyActiveCases.objects.filter(country=country, covid_data_date=date).first()
                    if not existing_db_entry or not existing_db_entry.active_cases_count:
                        request_string = f'https://covid-api.com/api/reports?iso={country_code}&date={date}'
                        r = requests.get(request_string)
                        if r.status_code in [200]:
                            covid_data = r.json()['data']
                            if covid_data:
                                print(f'Fetching {request_string}... OK')
                                active_cases_count = sum([province['active'] for province in covid_data])
                                rec = CovidMonthlyActiveCases(
                                    country=country,
                                    covid_data_date=date,
                                    active_cases_count=active_cases_count
                                )
                                rec.save()
                            else:
                                print(f'Fetching {request_string}... FAILED. NO DATA')
                                print(r.content)
                                rec = CovidMonthlyActiveCases(
                                    country=country,
                                    covid_data_date=date,
                                    active_cases_count=None
                                )
                                rec.save()
                                continue
                        else:
                            print(f'Fetching {request_string}... REQUEST FAILED')
                            print(r.status_code, r.content)
                            continue
                    else:
                        print(f'Data for {country_code} {date} already exists in database.')

