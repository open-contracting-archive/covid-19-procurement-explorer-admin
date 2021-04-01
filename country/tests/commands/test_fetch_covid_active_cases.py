import datetime
from io import StringIO
from textwrap import dedent
from unittest.mock import patch

from django.core.management import call_command
from django.test import TransactionTestCase

from country.models import Country, CovidMonthlyActiveCases


class CommandTests(TransactionTestCase):
    def assertCommand(self, *args, expected_out="", expected_err="", **kwargs):
        out = StringIO()
        err = StringIO()

        call_command(*args, **kwargs, stdout=out, stderr=out)

        self.assertEqual(err.getvalue(), dedent(expected_err))
        self.assertEqual(out.getvalue(), dedent(expected_out))

    def test_command(self):
        Country.objects.create(name="Global", country_code="GLO", country_code_alpha_2="gl", currency="USD")
        Country.objects.create(name="Kenya", country_code="KEN", country_code_alpha_2="KE", currency="KES")

        with patch("country.management.commands.fetch_covid_active_cases.datetime") as mock:
            mock.date.today.return_value = datetime.date(2020, 4, 30)
            mock.date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)

            self.assertCommand(
                "fetch_covid_active_cases",
                expected_out="""\
                    Fetching https://covid-api.com/api/reports?iso=KEN&date=2020-01-31... NO DATA
                    Fetching https://covid-api.com/api/reports?iso=KEN&date=2020-02-29... NO DATA
                    Fetching https://covid-api.com/api/reports?iso=KEN&date=2020-03-31... OK
                    Fetching https://covid-api.com/api/reports?iso=KEN&date=2020-04-30... OK
                """,
            )

            self.assertEqual(
                list(
                    CovidMonthlyActiveCases.objects.values_list(
                        "country__country_code", "covid_data_date", "active_cases_count", "death_count"
                    )
                ),
                [
                    ("KEN", datetime.date(2020, 3, 31), 57, 1),
                    ("KEN", datetime.date(2020, 4, 30), 235, 17),
                ],
            )

            self.assertCommand(
                "fetch_covid_active_cases",
                expected_out="""\
                    Fetching https://covid-api.com/api/reports?iso=KEN&date=2020-01-31... NO DATA
                    Fetching https://covid-api.com/api/reports?iso=KEN&date=2020-02-29... NO DATA
                """,
            )

            self.assertEqual(CovidMonthlyActiveCases.objects.count(), 2)
