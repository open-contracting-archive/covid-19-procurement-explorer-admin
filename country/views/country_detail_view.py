import socket

from django.db.models import Count, Max, Sum
from django.http import JsonResponse
from rest_framework.views import APIView

from country.models import Country, Tender


class CountryDetailView(APIView):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs["slug"]
        filter_args = {}
        filter_args["country__slug"] = slug

        country = Country.objects.filter(slug=slug).first()
        country_detail = []
        try:
            tender_data = Tender.objects.filter(**filter_args).aggregate(
                amount_usd=Sum("contract_value_usd"),
                amount_local=Sum("contract_value_local"),
                tender_count=Count("id"),
                contract_last_date=Max("contract_date"),
            )

            country_detail.append(
                {
                    "url": "https://" + socket.gethostbyname(socket.gethostname()) + "/api/v1/country/" + slug,
                    "id": country.id,
                    "continent": country.continent,
                    "amount_usd": tender_data["amount_usd"],
                    "amount_local": tender_data["amount_local"],
                    "tender_count": tender_data["tender_count"],
                    "last_contract_date": tender_data["contract_last_date"],
                    "slug": country.slug,
                    "name": country.name,
                    "population": country.population,
                    "gdp": country.gdp,
                    "country_code": country.country_code,
                    "country_code_alpha_2": country.country_code_alpha_2,
                    "currency": country.currency,
                    "healthcare_budget": country.healthcare_budget,
                    "healthcare_gdp_pc": country.healthcare_gdp_pc,
                    "covid_cases_total": country.covid_cases_total,
                    "covid_deaths_total": country.covid_deaths_total,
                    "covid_data_last_updated": country.covid_data_last_updated,
                }
            )
            return JsonResponse(country_detail, safe=False)
        except Exception:
            return JsonResponse([{"error": "Invalid country_code"}], safe=False)
