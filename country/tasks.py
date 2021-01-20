import requests
from requests.exceptions import Timeout
from django.conf import settings
from django.db import transaction
from datetime import datetime
from celery import Celery
# from celery import shared_task
import gspread
import sys, traceback
import pandas as pd
import random
import dateutil.parser
import math


from country.models import (
    Country,
    GoodsServicesCategory,
    GoodsServices,
    Buyer,
    Supplier, 
    Tender, 
    CurrencyConversionCache,
    EquityKeywords,
    EquityCategory
)

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
    if type(conversion_date)==str:
        conversion_date = dateutil.parser.parse(conversion_date).date()

    if not source_value or not source_currency or not conversion_date:
    # Missing Date: "" value has an invalid date format. It must be in YYYY-MM-DD format.
        return 0

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


def save_tender_excel_to_db(excel_file_path):
    total_rows_imported_count = 0
    errors = []

    try:
        ws_settings = pd.read_excel(excel_file_path, sheet_name='settings', header=None)
        ws_data = pd.read_excel(excel_file_path, sheet_name='data', header=0)

        country = ws_settings[2][1]
        currency = ws_settings[2][2]
    except Exception:
        traceback.print_exc(file=sys.stdout)
        return True

    for index, row in ws_data.iterrows():
        try:
            print(index,'...')
            contract_id = row['Contract ID']
            contract_date = row['Contract date (yyyy-mm-dd)'].date()

            procurement_procedure = random.choice([
                'open',
                'limited',
                'direct',
                'selective',
                ])    # row['Procurement procedure code']

            classification_code = row['CPV code clear']

            goods_services_category_name = row['Goods/Services'].strip()
            goods_services_category_desc = ''

            tender_value_local = row['Tender value'] or None
            award_value_local = row['Award value'] or None
            contract_value_local = row['Contract value'] or None

            contract_title = row['Contract title']
            contract_desc = row['Contract description']
            no_of_bidders = row['Number of bidders'] or None
            if math.isnan(no_of_bidders):
                no_of_bidders = None

            buyer_id = row['Buyer ID']
            buyer_name = row['Buyer']
            buyer_address = row['Buyer address (as an object)']

            supplier_id = row['Supplier ID']
            supplier_name = row['Supplier']
            supplier_address = row['Supplier address']

            status = random.choice([
                'active',
                'completed',
                'canceled',
                ])    # row['Contract Status Code']

            link_to_contract = row['Link to the contract']
            link_to_tender = ''    # row['Link to the tender']
            data_source = ''    # row['Data source']


            # Get Country
            country_obj = Country.objects.filter(name=country).first()

            # Get or Create Supplier
            if supplier_id:
                supplier_id = str(supplier_id).strip()
                supplier_obj = Supplier.objects.filter(supplier_id=supplier_id).first()
                if not supplier_obj:
                    supplier_obj = Supplier(
                        supplier_id = supplier_id,
                        supplier_name = supplier_name,
                        supplier_address = supplier_address,
                    )
                    supplier_obj.save()
            else:
                supplier_obj = None

            # Get or Create Buyer
            if buyer_id:
                buyer_id = str(buyer_id).strip()
                buyer_obj = Buyer.objects.filter(buyer_id=buyer_id).first()
                if not buyer_obj:
                    buyer_obj = Buyer(
                        buyer_id = buyer_id,
                        buyer_name = buyer_name,
                        buyer_address = buyer_address,
                    )
                    buyer_obj.save()
            else:
                buyer_obj = None

            # Get or Create Tender Contract
            if contract_id:
                contract_id = str(contract_id).strip()
                tender_obj = Tender.objects.filter(contract_id=contract_id).first()
                if not tender_obj:
                    tender_obj = Tender(
                        country=country_obj,
                        supplier=supplier_obj,
                        buyer=buyer_obj,

                        contract_id=contract_id,
                        contract_date=contract_date,
                        procurement_procedure=procurement_procedure,
                        status=status,
                        link_to_contract=link_to_contract,
                        link_to_tender=link_to_tender,
                        data_source=data_source,

                        # for viz api compatibility only; remove these later
                        contract_title=contract_title,
                        contract_value_local=contract_value_local or None,
                        contract_desc=contract_desc,
                        no_of_bidders=no_of_bidders or None,
                    )
                    tender_obj.save()
            else:
                tender_obj = None

            # Get or Create GoodsServicesCategory
            if goods_services_category_name:
                goods_services_category_obj = GoodsServicesCategory.objects.filter(category_name=goods_services_category_name).first()
                if not goods_services_category_obj:
                    goods_services_category_obj = GoodsServicesCategory(
                        category_name = goods_services_category_name,
                        category_desc = goods_services_category_desc
                    )
                    goods_services_category_obj.save()
            else:
                goods_services_category_obj = None


            # Create GoodsServices...

            if tender_obj:
            # ...only if there is a contract that it can be associated with
                goods_services_obj = GoodsServices(
                    country=country_obj,
                    goods_services_category = goods_services_category_obj,
                    contract = tender_obj,
                    
                    classification_code = classification_code,
                    no_of_bidders = no_of_bidders or None,
                    contract_title = contract_title,
                    contract_desc = contract_desc,
                    tender_value_local = tender_value_local or None,
                    award_value_local = award_value_local or None,
                    contract_value_local = contract_value_local or None,
                )
                goods_services_obj.save()

                print(tender_obj.id, goods_services_obj.id)

                # Execute local currency to USD conversion celery tasks
                conversion_date = contract_date
                source_currency = country_obj.currency
                source_values = {
                    'tender_value_local': tender_value_local or None,
                    'award_value_local': award_value_local or None,
                    'contract_value_local': contract_value_local or None,
                }
                goods_services_row_id = goods_services_obj.id
                local_currency_to_usd.apply_async(args=(
                    goods_services_row_id,
                    conversion_date,
                    source_currency,
                    source_values
                    ), queue='covid19')

            total_rows_imported_count += 1
        except Exception:
            # transaction.rollback()

            contract_id = row['Contract ID']
            errors.append((index,contract_id))
            print('------------------------------')
            print(f'Error importing row {index}, contract id {contract_id}')
            print(f'{row}\n')
            traceback.print_exc(file=sys.stdout)
            print('------------------------------')
    

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

        data_all = worksheet_data.get_all_records()

        data = []
        for i in data_all:    
            if not i['Contract ID'] and not i['Contract date (yyyy-mm-dd)'] and not i['Contract value']:
            # detect end of rows
                break
            else:
                data.append(i)

        total_rows_imported_count = 0
        errors = []

        for index, row in enumerate(data):
            # with transaction.atomic():
                try:
                    #### TODO: Check if row already exists in database
                    ##
                    ##


                    # Get Country
                    country_obj = Country.objects.filter(name=country).first()

                    # Get or Create Supplier
                    supplier_id = row['Supplier ID']
                    supplier_name = row['Supplier']
                    supplier_address = row['Supplier address']

                    if supplier_id:
                        supplier_id = str(supplier_id).strip()
                        supplier_obj = Supplier.objects.filter(supplier_id=supplier_id).first()
                        if not supplier_obj:
                            supplier_obj = Supplier(
                                supplier_id = supplier_id,
                                supplier_name = supplier_name,
                                supplier_address = supplier_address,
                            )
                            supplier_obj.save()
                    else:
                        supplier_obj = None

                    # Get or Create Buyer
                    buyer_id = row['Buyer ID']
                    buyer_name = row['Buyer']
                    buyer_address = row['Buyer address (as an object)']

                    if buyer_id:
                        buyer_id = str(buyer_id).strip()
                        buyer_obj = Buyer.objects.filter(buyer_id=buyer_id).first()
                        if not buyer_obj:
                            buyer_obj = Buyer(
                                buyer_id = buyer_id,
                                buyer_name = buyer_name,
                                buyer_address = buyer_address,
                            )
                            buyer_obj.save()
                    else:
                        buyer_obj = None


                    # Get or Create Tender Contract
                    contract_id = row['Contract ID']

                    if contract_id:
                        contract_id = str(contract_id).strip()
                        tender_obj = Tender.objects.filter(contract_id=contract_id).first()
                        if not tender_obj:
                            tender_obj = Tender(
                                country=country_obj,
                                supplier=supplier_obj,
                                buyer=buyer_obj,

                                contract_id=row['Contract ID'],
                                contract_date=row['Contract date (yyyy-mm-dd)'],
                                procurement_procedure=row['Procurement procedure code'],
                                status=row['Contract Status Code'],
                                link_to_contract=row['Link to the contract'],
                                link_to_tender=row['Link to the tender'],
                                data_source=row['Data source'],

                                # for viz api compatibility only; remove these later
                                contract_title=row['Contract title'],
                                contract_value_local=row['Contract value'] or None,
                                contract_desc=row['Contract description'],
                                no_of_bidders=row['Number of bidders'] or None,
                            )
                            tender_obj.save()
                    else:
                        tender_obj = None

                    # Get or Create GoodsServicesCategory
                    goods_services_category_name = row['Goods/Services'].strip()
                    goods_services_category_desc = ''

                    if goods_services_category_name:
                        goods_services_category_obj = GoodsServicesCategory.objects.filter(category_name=goods_services_category_name).first()
                        if not goods_services_category_obj:
                            goods_services_category_obj = GoodsServicesCategory(
                                category_name = goods_services_category_name,
                                category_desc = goods_services_category_desc
                            )
                            goods_services_category_obj.save()
                    else:
                        goods_services_category_obj = None


                    # Create GoodsServices...

                    if tender_obj:
                    # ...only if there is a contract that it can be associated with
                        goods_services_obj = GoodsServices(
                            country=country_obj,
                            goods_services_category = goods_services_category_obj,
                            contract = tender_obj,
                            
                            classification_code = row['Classification Code (CPV or other)'],
                            no_of_bidders = row['Number of bidders'] or None,
                            contract_title = row['Contract title'],
                            contract_desc = row['Contract description'],
                            tender_value_local = row['Tender value'] or None,
                            award_value_local = row['Award value'] or None,
                            contract_value_local = row['Contract value'] or None,
                        )
                        goods_services_obj.save()

                        print(tender_obj.id, goods_services_obj.id)

                        # Execute local currency to USD conversion celery tasks
                        conversion_date = row['Contract date (yyyy-mm-dd)']
                        source_currency = country_obj.currency
                        source_values = {
                            'tender_value_local': row['Tender value'] or None,
                            'award_value_local': row['Award value'] or None,
                            'contract_value_local': row['Contract value'] or None,
                        }
                        goods_services_row_id = goods_services_obj.id
                        local_currency_to_usd.apply_async(args=(
                            goods_services_row_id,
                            conversion_date,
                            source_currency,
                            source_values
                            ), queue='covid19')

                    total_rows_imported_count += 1
                except Exception:
                    # transaction.rollback()

                    contract_id = row['Contract ID']
                    errors.append((index,contract_id))
                    print('------------------------------')
                    print(f'Error importing row {index}, contract id {contract_id}')
                    print(f'{row}\n')
                    traceback.print_exc(file=sys.stdout)
                    print('------------------------------')

        print(f'Total rows imported: {total_rows_imported_count}')
        print(errors)
    except Exception as e:
        print(e)


@app.task(name='import_tender_data')
def import_tender_data(gs_sheet_url):
    print(f'import_tender_data from {gs_sheet_url}')
    save_tender_data_to_db(gs_sheet_url)


@app.task(name='import_tender_data_excel')
def import_tender_data_excel(excel_file_path):
    print(f'import_tender_data from {excel_file_path}')
    save_tender_excel_to_db(excel_file_path)


@app.task(name='local_currency_to_usd')
def local_currency_to_usd(goods_services_row_id, conversion_date, source_currency, source_values):
    # source_values = {
    #     'tender_value_local': row['Tender value'],
    #     'award_value_local': row['Award value'],
    #     'contract_value_local': row['Contract value']
    # }
    
    dst_tender_value = convert_local_to_usd(conversion_date, source_currency, source_values['tender_value_local'], dst_currency='USD')
    dst_award_value = convert_local_to_usd(conversion_date, source_currency, source_values['award_value_local'], dst_currency='USD')
    dst_contract_value = convert_local_to_usd(conversion_date, source_currency, source_values['contract_value_local'], dst_currency='USD')

    r = GoodsServices.objects.filter(id=goods_services_row_id).first()
    if r:
        r.tender_value_usd = dst_tender_value or None
        r.award_value_usd = dst_award_value or None
        r.contract_value_usd = dst_contract_value or None
        r.save()

@app.task(name='fetch_equity_data')
def fetch_equity_data(country):
    country_instance = Country.objects.get(name=country)
    tenders = Tender.objects.filter(country=country_instance)
    keywords = EquityKeywords.objects.filter(country=country_instance)
    for tender in tenders:
        goodservices = tender.goods_services.filter(country=country_instance)
        for good_service in goodservices:
            print(good_service.id)
            for keyword in keywords:
                keyword_value = keyword.keyword
                if keyword_value in good_service.contract_title.strip() or keyword_value in good_service.contract_desc.strip():
                    category = keyword.equity_category.category_name
                    print(category)
                    instance = EquityCategory.objects.get(category_name=category)
                    tender.equity_category.add(instance)


@app.task(name='process_currency_conversion')
def process_currency_conversion(tender_value_local,award_value_local,contract_value_local,tender_date,currency,id):
    tender_value_usd = convert_local_to_usd(source_value=tender_value_local,conversion_date=tender_date,source_currency=currency) if tender_value_local else None
    award_value_usd = convert_local_to_usd(source_value=award_value_local,conversion_date=tender_date,source_currency=currency) if award_value_local else None
    contract_value_usd = convert_local_to_usd(source_value=contract_value_local,conversion_date=tender_date,source_currency=currency) if contract_value_local else None
    print(f'started processing... {id}: {tender_value_usd}, {award_value_usd}, {contract_value_usd}')
    if tender_value_usd or award_value_usd or contract_value_usd:
        tender = GoodsServices.objects.get(id=id)
        tender.tender_value_usd = tender_value_usd
        tender.award_value_usd = award_value_usd
        tender.contract_value_usd = contract_value_usd
        tender.save()
        print('Converted goodsservices id:'+ str(tender.id))
    print(f'end of {id}')