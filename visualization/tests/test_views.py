from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from content.models import CountryPartner
from country.models import Buyer, Country, DataProvider, Language, Supplier, Tender, Topic


def setUpModule():
    call_command("loaddata", "country", "redflag", "equitycategory", "equitykeywords")
    Language.objects.create(
        name="english",
        code="en",
    )
    Topic.objects.create(title="corona virus")
    supplier = Supplier.objects.create(
        supplier_id="1",
        supplier_name="sample supplier",
        supplier_address="kathmandu",
    )

    buyer = Buyer.objects.create(
        buyer_id="1",
        buyer_name="sample buyer",
        buyer_address="kathmandu",
    )

    Tender.objects.create(
        country=Country.objects.all().first(),
        supplier=supplier,
        buyer=buyer,
        contract_id=1,
        contract_date="2021-01-01",
        procurement_procedure="open",
        status="active",
        link_to_contract="http://test.com",
        link_to_tender="http://test.com",
        data_source="http://test.com",
        no_of_bidders=1,
        contract_title="test",
        contract_value_local=1.0,
        contract_value_usd=1.0,
        contract_desc="test description",
        tender_value_local=1.0,
        tender_value_usd=1.0,
        award_value_local=1.0,
        award_value_usd=1.0,
    )

    CountryPartner.objects.create(
        name="Kenya",
        description="country description",
        country=Country.objects.get(country_code_alpha_2="KE"),
        email="country@email.com",
        website="example.com",
        logo="country/partner/logo/gl.jpg",
    )

    DataProvider.objects.create(
        name="",
        country=Country.objects.get(country_code_alpha_2="KE"),
        website="example.com",
        logo="country/partner/logo/gl.jpg",
        remark="country description",
    )


class VisualizationViewTest(TestCase):
    def setUp(self):
        self.average_bids_url = "average_bids"
        self.buyer_detail_url = "buyer_detail"
        self.buyer_summary_url = "buyer_summary"
        self.buyer_trend_url = "buyer_trend"
        self.contract_red_flags_url = "contract_red_flags"
        self.contract_status_url = "contract_status"
        self.country_map_api_url = "country_map_api"
        self.country_map_url = "country_map"
        self.country_partners_url = "country_partners"
        self.country_suppliers_url = "country_suppliers"
        self.data_providers_url = "data_providers"
        self.direct_open_contract_trend_url = "direct_open_contract_trend"
        self.direct_open_url = "direct_open"
        self.equity_indicators_url = "equity_indicators"
        self.equity_summary_url = "equity_summary"
        self.filter_parameters_url = "filter_parameters"
        self.filters_parameters_buyers_url = "filters_parameters_buyers"
        self.filters_parameters_static_url = "filters_parameters_static"
        self.filters_parameters_suppliers_url = "filters_parameters_suppliers"
        self.global_suppliers_url = "global_suppliers"
        self.monopolization_url = "monopolization"
        self.product_distribution_url = "product_distribution"
        self.product_flow_view_url = "product_flow_view"
        self.product_spending_comparison_url = "product_spending_comparison"
        self.product_summary_url = "product_summary"
        self.product_timeline_race_url = "product_timeline_race"
        self.product_timeline_url = "product_timeline"
        self.products_url = "products"
        self.quantity_correlation_url = "quantity_correlation"
        self.red_flag_summary_url = "red_flag_summary"
        self.supplier_detail_url = "supplier_detail"
        self.supplier_flow_view_url = "supplier_flow_view"
        self.supplier_summary_url = "supplier_summary"
        self.supplier_trend_url = "supplier_trend"
        self.top_buyers_url = "top_buyers"
        self.top_suppliers_url = "top_suppliers"
        self.total_contract_list_url = "total_contracts"
        self.total_contracts_url = "total_contracts"
        self.total_spending_url = "total_spending"
        self.world_map_race_url = "world_map_race"
        self.world_map_url = "world_map"

    def test_total_contracts_GET(self):
        url = "%s?country=KE&buyer=1&supplier=1" % reverse(self.total_contracts_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_total_spending_GET(self):
        url = "%s?country=KE&buyer=1&supplier=1" % reverse(self.total_spending_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_average_bids_GET(self):
        url = "%s?country=KE&buyer=1" % reverse(self.average_bids_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_world_map_race_GET(self):
        response = self.client.get(reverse(self.world_map_race_url))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_top_suppliers_GET(self):
        response = self.client.get(reverse(self.top_suppliers_url))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_top_buyers_GET(self):
        response = self.client.get(reverse(self.top_buyers_url))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_direct_open_GET(self):
        url = "%s?country=KE&buyer=1&supplier=1" % reverse(self.direct_open_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_direct_open_all_GET(self):
        url = reverse(self.direct_open_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_contract_status_GET(self):
        url = "%s?country=KE&buyer=1" % reverse(self.contract_status_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_quantity_correlation_GET(self):
        url = "%s?country=KE" % reverse(self.quantity_correlation_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_monopolization_GET(self):
        url = "%s?country=KE&buyer=1" % reverse(self.monopolization_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_country_suppliers_GET(self):
        url = "%s?country=KE" % reverse(self.country_suppliers_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_country_map_GET(self):
        url = "%s?country=KE" % reverse(self.country_map_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_world_map_GET(self):
        url = "%s?product=1" % reverse(self.world_map_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_country_map_api_GET(self):
        url = "%s?country=KE" % reverse(self.country_map_api_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_invalid_country_map_api_GET(self):
        url = "%s?country=AB" % reverse(self.country_map_api_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_global_suppliers_GET(self):
        response = self.client.get(reverse(self.global_suppliers_url))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_product_distribution_GET(self):
        url = "%s?country=KE&buyer=1" % reverse(self.product_distribution_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_equity_indicators_GET(self):
        url = "%s?country=KE&buyer=1" % reverse(self.equity_indicators_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_product_timeline_GET(self):
        url = "%s?country=KE&buyer=1&supplier=1" % reverse(self.product_timeline_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_product_timeline_race_GET(self):
        response = self.client.get(reverse(self.product_timeline_race_url))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_supplier_detail_GET(self):
        response = self.client.get(reverse(self.supplier_detail_url, args=["1"]))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_buyer_detail_GET(self):
        response = self.client.get(reverse(self.buyer_detail_url, args=[1]))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_buyer_detail_failed_GET(self):
        response = self.client.get(reverse(self.buyer_detail_url, args=[99999]))
        self.assertEquals(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_country_partners_GET(self):
        url = "%s?country=KE" % reverse(self.country_partners_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_all_country_partners_GET(self):
        url = reverse(self.country_partners_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_data_providers_GET(self):
        url = "%s?country=KE" % reverse(self.data_providers_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_data_providers_all_GET(self):
        url = reverse(self.data_providers_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_buyer_summary_GET(self):
        url = "%s?country=gl" % reverse(self.buyer_summary_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_supplier_summary_GET(self):
        url = "%s?country=KE" % reverse(self.supplier_summary_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_filter_parameters_GET(self):
        response = self.client.get(reverse(self.filter_parameters_url))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_product_summary_GET(self):
        url = "%s?country=KE" % reverse(self.product_summary_url)
        response = self.client.get(url)
        print(response.json())
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_equity_summary_GET(self):
        url = "%s?country=KE" % reverse(self.equity_summary_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_products_GET(self):
        url = "%s?country=KE&buyer=1" % reverse(self.products_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_filters_parameters_suppliers_GET(self):
        url = "%s?country=KE&buyer=1" % reverse(self.filters_parameters_suppliers_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_filters_parameters_buyers_GET(self):
        url = "%s?country=KE&supplier=1" % reverse(self.filters_parameters_buyers_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_filters_parameters_static_GET(self):
        response = self.client.get(reverse(self.filters_parameters_static_url))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_product_spending_comparison_GET(self):
        url = "%s?product=1" % reverse(self.product_spending_comparison_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_buyer_trend_GET(self):
        response = self.client.get(reverse(self.buyer_trend_url))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_supplier_trend_GET(self):
        response = self.client.get(reverse(self.supplier_trend_url))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_direct_open_contract_trend_GET(self):
        response = self.client.get(reverse(self.direct_open_contract_trend_url))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_contract_red_flags_GET(self):
        url = "%s?country=KE&buyer=1&supplier=1&product=1" % reverse(self.contract_red_flags_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_red_flag_summary_GET(self):
        response = self.client.get(reverse(self.red_flag_summary_url))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_product_flow_view_GET(self):
        url = reverse(self.product_flow_view_url, args=["1"])
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_supplier_flow_view_GET(self):
        url = reverse(self.supplier_flow_view_url, args=["1"])
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
