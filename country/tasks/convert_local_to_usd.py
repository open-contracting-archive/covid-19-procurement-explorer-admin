import dateutil.parser
import requests
from celery import Celery
from django.conf import settings
from requests.exceptions import Timeout

from country.models import CurrencyConversionCache

app = Celery()


def convert_local_to_usd(conversion_date, source_currency, source_value, dst_currency="USD"):
    if type(conversion_date) == str:
        conversion_date = dateutil.parser.parse(conversion_date).date()

    if not source_value or not source_currency or not conversion_date:
        # Missing Date: "" value has an invalid date format. It must be in YYYY-MM-DD format.
        return 0

    result = CurrencyConversionCache.objects.filter(
        conversion_date=conversion_date, source_currency=source_currency, dst_currency=dst_currency
    ).first()

    if result:
        return round(source_value * result.conversion_rate, 2)
    else:
        access_key = settings.FIXER_IO_API_KEY

        try:
            r = requests.get(
                f"https://data.fixer.io/api/{conversion_date}?access_key={access_key}&base={source_currency}"
                f"&symbols={dst_currency}",
                timeout=20,
            )
            # A sample response:
            #
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
                if fixer_data["success"]:
                    conversion_rate = fixer_data["rates"][dst_currency]
                    dst_value = round(source_value * conversion_rate, 2)

                    c = CurrencyConversionCache(
                        source_currency=source_currency,
                        dst_currency=dst_currency,
                        conversion_date=conversion_date,
                        conversion_rate=conversion_rate,
                    )
                    c.save()

                    return dst_value
        except Timeout:
            return 0
