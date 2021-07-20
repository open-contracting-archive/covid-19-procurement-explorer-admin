from celery import Celery

from country.models import Country, EquityCategory, EquityKeywords, Tender

app = Celery()


@app.task(name="evaluate_contract_equity")
def evaluate_contract_equity(country_code):
    country = Country.objects.get(country_code_alpha_2=country_code)
    contracts = Tender.objects.filter(country=country)
    equity_keywords = EquityKeywords.objects.filter(country=country)

    for contract in contracts:
        for good_service in contract.goods_services:
            for keyword in equity_keywords:
                keyword_value = keyword.keyword

                if (
                    keyword_value in good_service.contract_title.strip()
                    or keyword_value in good_service.contract_desc.strip()
                ):
                    category = keyword.equity_category.category_name
                    instance = EquityCategory.objects.get(category_name=category)
                    contract.equity_category.add(instance)
