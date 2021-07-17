from celery import Celery

from country.models import Country, EquityCategory, EquityKeywords, Tender

app = Celery()


@app.task(name="evaluate_contract_equity")
def evaluate_contract_equity(country_code):
    country = Country.objects.get(country_code_alpha_2=country_code)
    tenders = Tender.objects.filter(country=country)
    equity_keywords = EquityKeywords.objects.filter(country=country)

    for tender in tenders:
        good_services = tender.goods_services.filter(country=country)

        for good_service in good_services:
            print(good_service.id)

            for keyword in equity_keywords:
                keyword_value = keyword.keyword

                if (
                    keyword_value in good_service.contract_title.strip()
                    or keyword_value in good_service.contract_desc.strip()
                ):
                    category = keyword.equity_category.category_name
                    print(category)
                    instance = EquityCategory.objects.get(category_name=category)
                    tender.equity_category.add(instance)
