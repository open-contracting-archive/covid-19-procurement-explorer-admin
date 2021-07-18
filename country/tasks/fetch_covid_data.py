import datetime

import requests
from celery import Celery
from requests.exceptions import Timeout

from country.models import Country

app = Celery()


@app.task(name="fetch_covid_data")
def fetch_covid_data():
    countries = Country.objects.all()

    for country in countries:
        country_code = country.country_code

        if country_code:
            try:
                r = requests.get(f"https://covid-api.com/api/reports?iso={country_code}", timeout=20)
                if r.status_code in [200]:
                    # if country_code is invalid r.json() is {'data': []}
                    covid_data = r.json()["data"]

                    if covid_data:
                        covid_cases_total = sum([province["confirmed"] for province in covid_data])
                        covid_deaths_total = sum([province["deaths"] for province in covid_data])

                        country.covid_cases_total = covid_cases_total
                        country.covid_deaths_total = covid_deaths_total
                        country.covid_data_last_updated = datetime.now()
                        country.save()
            except Timeout:
                continue
