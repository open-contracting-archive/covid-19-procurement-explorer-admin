import calendar
import datetime

import requests
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.management.base import BaseCommand

from country.models import Country, CovidMonthlyActiveCases


class Command(BaseCommand):
    help = "Fetch Covid-19 case statistics from covid-api.com"

    def handle(self, *args, **kwargs):
        today = datetime.date.today()
        dates_in_period = set()

        for year in range(2020, today.year + 1):
            for month in range(1, 13):
                day = calendar.monthrange(year, month)[1]
                date = datetime.date(year, month, day)
                if date > today:
                    break
                dates_in_period.add(date)

        # If a country has no dates, the list will be `[None]`.
        dates_with_data = dict(
            Country.objects.exclude(country_code_alpha_2="gl")
            .prefetch_related("covid_monthly_active_cases")
            .annotate(date=ArrayAgg("covid_monthly_active_cases__covid_data_date"))
            .values_list("country_code", "date")
        )
        countries = Country.objects.all().exclude(country_code_alpha_2="gl").order_by("country_code")

        for country in countries:
            country_code = country.country_code
            country_dates = set(dates_with_data[country_code])
            dates_to_query = dates_in_period - country_dates
            minimum_date = min(country_dates)

            url = f"https://covid-api.com/api/reports/total?iso={country_code}"
            print(country_code)
            response = requests.get(url)
            data = response.json()["data"]

            if not data:
                self.stdout.write(f"Fetching {url}... NO DATA")
                active_cases = 0
                total_cases = 0
                total_death = 0
            else:
                active_cases = data["active"]
                total_cases = data["confirmed"]
                total_death = data["deaths"]

            Country.objects.filter(country_code=country_code).update(
                covid_active_cases=active_cases, covid_deaths_total=total_death, covid_cases_total=total_cases
            )

            for date in sorted(dates_to_query):
                # Don't retry dates from the beginning of the pandemic.
                if minimum_date and date < minimum_date:
                    continue

                url = f"https://covid-api.com/api/reports?iso={country_code}&date={date}"

                response = requests.get(url)

                if not response.ok:
                    self.stderr.write(f"Fetching {url}... {response.status_code}")
                    continue

                data = response.json()["data"]

                if not data:
                    self.stdout.write(f"Fetching {url}... NO DATA")
                    continue

                active_cases_count = 0
                death_count = 0

                for item in data:
                    active_cases_count += item["active"]
                    death_count += item["deaths"]

                CovidMonthlyActiveCases(
                    country=country,
                    covid_data_date=date,
                    active_cases_count=active_cases_count,
                    death_count=death_count,
                ).save()

                self.stdout.write(f"Fetching {url}... OK")
