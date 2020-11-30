import requests
from requests.exceptions import Timeout
from django.conf import settings
from datetime import datetime
from celery import Celery
# from celery import shared_task
import gspread
import sys, traceback


from country.models import Country, Supplier, Tender, CurrencyConversionCache

app = Celery()


@app.task(name='fetch_covid_data')
def fetch_covid_data():
    countries = Country.objects.all()

    for country in countries:
        country_code = country.country_code

        if country_code:
            try:
                r = requests.get(f'https://covid-api.com/api/reports?iso={country_code}', timeout=20)
                if r.status_code in [200]:
                    # if country_code is invalid r.json() is {'data': []}
                    covid_data = r.json()['data']

                    if covid_data:
                        covid_cases_total = sum([province['confirmed'] for province in covid_data])
                        covid_deaths_total = sum([province['deaths'] for province in covid_data])

                        country.covid_cases_total = covid_cases_total
                        country.covid_deaths_total = covid_deaths_total
                        country.covid_data_last_updated = datetime.now()
                        country.save()
            except Timeout:
                continue


def convert_local_to_usd(conversion_date, source_currency, source_value, dst_currency='USD'):
    result = CurrencyConversionCache.objects.filter(
        conversion_date=conversion_date,
        source_currency=source_currency,
        dst_currency=dst_currency
        ).first()

    if result:
        print('Found conversion data in database')
        conversion_rate = result.conversion_rate
        dst_value = round(source_value*conversion_rate,2)
        return dst_value
    else:
        print('Fetching conversion data from fixer.io')
        access_key = settings.FIXER_IO_API_KEY
        try:
            r = requests.get(f'https://data.fixer.io/api/{conversion_date}?access_key={access_key}&base={source_currency}&symbols={dst_currency}', timeout=20)
            # {
            #     "success": true,
            #     "timestamp": 1387929599,
            #     "historical": true,
            #     "base": "MXN",
            #     "date": "2013-12-24",
            #     "rates": {
            #         "USD": 0.076811
            #     }
            # }
            if r.status_code in [200]:
                fixer_data = r.json()
                if fixer_data['success']:
                    conversion_rate = fixer_data['rates'][dst_currency]
                    dst_value = round(source_value*conversion_rate, 2)

                    c = CurrencyConversionCache(
                        source_currency=source_currency,
                        # source_value=source_value,
                        dst_currency=dst_currency,
                        # dst_value=dst_value,
                        conversion_date=conversion_date,
                        conversion_rate=conversion_rate
                    )
                    c.save()

                    return dst_value
        except Timeout:
            return None


def save_tender_data_to_db(gs_sheet_url):
    contract_ids = []
    duplicate_contract_ids = []

    gc = gspread.service_account(filename=settings.GOOGLE_SHEET_CREDENTIALS_JSON)
    covid_sheets = gc.open_by_url(gs_sheet_url)

    try:
        worksheet_settings = covid_sheets.worksheet('settings')
        worksheet_codelist = covid_sheets.worksheet('codelist')
        worksheet_data = covid_sheets.worksheet('data')

        # Get country and currency from worksheet:settings
        country = worksheet_settings.cell(2,3).value
        currency = worksheet_settings.cell(3,3).value

        procurement_start_row=5
        contract_status_row=5

        procurement_method_map = {}
        contract_status_map = {}

        while True:
            title_lang = worksheet_codelist.cell(procurement_start_row,2).value
            title_code = worksheet_codelist.cell(procurement_start_row,4).value
            if title_lang and title_code:
                procurement_method_map[title_lang]=title_code
            if not title_lang and not title_code:
                break
            procurement_start_row+=1

        while True:
            title_lang = worksheet_codelist.cell(contract_status_row,7).value
            title_code = worksheet_codelist.cell(contract_status_row,9).value
            if title_lang and title_code:
                contract_status_map[title_lang]=title_code
            if not title_lang and not title_code:
                break
            contract_status_row+=1

        data = worksheet_data.get_all_records()

        data_converted = []

        for i in data:    
            if not i['Contract ID']:
                break
            # print(i['Contract ID'], i['Procurement procedure'], i['Contract Status'])
            if i['Procurement procedure']:
                i['Procurement procedure'] = procurement_method_map[i['Procurement procedure']]
            if i['Contract Status']:
                i['Contract Status'] = contract_status_map[i['Contract Status']]
            data_converted.append(i)

        country_obj = Country.objects.filter(name=country).first()
        for index, row in enumerate(data_converted):  
            try:  
                supplier_obj = Supplier.objects.filter(supplier_id=row['Supplier ID'],supplier_name=row['Supplier']).first()
                if not supplier_obj:
                    supplier_obj = Supplier(
                        supplier_id = row['Supplier ID'],
                        supplier_name = row['Supplier']
                    )
                    supplier_obj.save()
            
                tender_obj = Tender(
                    country=country_obj,
                    supplier=supplier_obj,
                    contract_id=row['Contract ID'],
                    contract_date=row['Contract date (yyyy-mm-dd)'],
                    contract_title=row['Contract title'],
                    contract_value_local=row['Contract value'],
                    contract_desc=row['Contract description'],
                    procurement_procedure=row['Procurement procedure code'],
                    status='active',
                    link_to_contract=row['Link to the contract'],
                    link_to_tender=row['Link to the tender'],
                    data_source=row['Data source'],
                )
                tender_obj.save()
                print(tender_obj.id)

                conversion_date = row['Contract date (yyyy-mm-dd)']
                source_currency = country_obj.currency
                source_value = row['Contract value']
                local_currency_to_usd.apply_async(args=(
                    tender_obj.id,
                    conversion_date,
                    source_currency,
                    source_value
                    ), queue='covid19')

                if row['Contract ID'] in contract_ids:
                    duplicate_contract_ids.append((index, row['Contract ID']))
                else:
                    contract_ids.append(row['Contract ID'])
            except Exception:
                contract_id = row['Contract ID']
                print(f'Error importing row {index}, contract id {contract_id}')
                traceback.print_exc(file=sys.stdout)

    except Exception as e:
        print(e)

    print(duplicate_contract_ids)


@app.task(name='import_tender_data')
def import_tender_data(gs_sheet_url):
    print(f'import_tender_data from {gs_sheet_url}')
    save_tender_data_to_db(gs_sheet_url)


@app.task(name='local_currency_to_usd')
def local_currency_to_usd(tender_row_id, conversion_date, source_currency, source_value):
    dst_value = convert_local_to_usd(conversion_date, source_currency, source_value, dst_currency='USD')

    r = Tender.objects.filter(id=tender_row_id).first()
    if r:
        r.contract_value_usd = dst_value
        r.save()
