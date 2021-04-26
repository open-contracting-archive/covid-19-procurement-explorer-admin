from django.test import TestCase
from django.urls import reverse


class VisualizationViewTest(TestCase):
    def setUp(self):
        self.total_contract_list_url = "total_contracts"
        self.total_contracts_url = "total_contracts"
        self.total_spending_url = "total_spending"
        self.average_bids_url = "average_bids"
        self.world_map_race_url = "world_map_race"
        self.top_suppliers_url = "top_suppliers"
        self.top_buyers_url = "top_buyers"
        self.direct_open_url = "direct_open"
        self.contract_status_url = "contract_status"
        self.quantity_correlation_url = "quantity_correlation"
        self.monopolization_url = "monopolization"
        self.country_suppliers_url = "country_suppliers"
        self.country_map_url = "country_map"
        self.world_map_url = "world_map"
        self.country_map_api_url = "country_map_api"
        self.global_suppliers_url = "global_suppliers"
        self.product_distribution_url = "product_distribution"
        self.equity_indicators_url = "equity_indicators"
        self.product_timeline_url = "product_timeline"
        self.product_timeline_race_url = "product_timeline_race"
        self.supplier_detail_url = "supplier_detail"
        self.buyer_detail_url = "buyer_detail"
        self.country_partners_url = "country_partners"
        self.data_providers_url = "data_providers"
        self.buyer_summary_url = "buyer_summary"
        self.supplier_summary_url = "supplier_summary"
        self.filter_parameters_url = "filter_parameters"
        self.product_summary_url = "product_summary"
        self.equity_summary_url = "equity_summary"
        self.products_url = "products"
        self.filters_parameters_suppliers_url = "filters_parameters_suppliers"
        self.filters_parameters_buyers_url = "filters_parameters_buyers"
        self.filters_parameters_static_url = "filters_parameters_static"
        self.product_spending_comparison_url = "product_spending_comparison"
        self.buyer_trend_url = "buyer_trend"
        self.supplier_trend_url = "supplier_trend"
        self.direct_open_contract_trend_url = "direct_open_contract_trend"
        self.contract_red_flags_url = "contract_red_flags"
        self.red_flag_summary_url = "red_flag_summary"

    def test_total_contracts_GET(self):
        response = self.client.get(reverse(self.total_contracts_url))
        self.assertEquals(response.status_code, 200)

    def test_total_spending_GET(self):
        response = self.client.get(reverse(self.total_spending_url))
        self.assertEquals(response.status_code, 200)

    def test_average_bids_GET(self):
        response = self.client.get(reverse(self.average_bids_url))
        self.assertEquals(response.status_code, 200)

    def test_world_map_race_GET(self):
        response = self.client.get(reverse(self.world_map_race_url))
        self.assertEquals(response.status_code, 200)

    def test_top_suppliers_GET(self):
        response = self.client.get(reverse(self.top_suppliers_url))
        self.assertEquals(response.status_code, 200)

    def test_top_buyers_GET(self):
        response = self.client.get(reverse(self.top_buyers_url))
        self.assertEquals(response.status_code, 200)

    def test_direct_open_GET(self):
        response = self.client.get(reverse(self.direct_open_url))
        self.assertEquals(response.status_code, 200)

    def test_contract_status_GET(self):
        response = self.client.get(reverse(self.contract_status_url))
        self.assertEquals(response.status_code, 200)

    def test_quantity_correlation_GET(self):
        response = self.client.get(reverse(self.quantity_correlation_url))
        self.assertEquals(response.status_code, 200)

    def test_monopolization_GET(self):
        response = self.client.get(reverse(self.monopolization_url))
        self.assertEquals(response.status_code, 200)

    def test_country_suppliers_GET(self):
        response = self.client.get(reverse(self.country_suppliers_url))
        self.assertEquals(response.status_code, 200)

    def test_country_map_GET(self):
        response = self.client.get(reverse(self.country_map_url))
        self.assertEquals(response.status_code, 200)

    def test_world_map_GET(self):
        response = self.client.get(reverse(self.world_map_url))
        self.assertEquals(response.status_code, 200)

    def test_country_map_api_GET(self):
        response = self.client.get(reverse(self.country_map_api_url))
        self.assertEquals(response.status_code, 200)

    def test_global_suppliers_GET(self):
        response = self.client.get(reverse(self.global_suppliers_url))
        self.assertEquals(response.status_code, 200)

    def test_product_distribution_GET(self):
        response = self.client.get(reverse(self.product_distribution_url))
        self.assertEquals(response.status_code, 200)

    def test_equity_indicators_GET(self):
        response = self.client.get(reverse(self.equity_indicators_url))
        self.assertEquals(response.status_code, 200)

    def test_product_timeline_GET(self):
        response = self.client.get(reverse(self.product_timeline_url))
        self.assertEquals(response.status_code, 200)

    def test_product_timeline_race_GET(self):
        response = self.client.get(reverse(self.product_timeline_race_url))
        self.assertEquals(response.status_code, 200)

    def test_supplier_detail_GET(self):
        response = self.client.get(reverse(self.supplier_detail_url, args=["1"]))
        self.assertEquals(response.status_code, 200)

    def test_buyer_detail_GET(self):
        response = self.client.get(reverse(self.buyer_detail_url, args=["1"]))
        self.assertEquals(response.status_code, 200)

    def test_country_partners_GET(self):
        response = self.client.get(reverse(self.country_partners_url))
        self.assertEquals(response.status_code, 200)

    def test_data_providers_GET(self):
        response = self.client.get(reverse(self.data_providers_url))
        self.assertEquals(response.status_code, 200)

    def test_buyer_summary_GET(self):
        response = self.client.get(reverse(self.buyer_summary_url))
        self.assertEquals(response.status_code, 200)

    def test_supplier_summary_GET(self):
        response = self.client.get(reverse(self.supplier_summary_url))
        self.assertEquals(response.status_code, 200)

    def test_filter_parameters_GET(self):
        response = self.client.get(reverse(self.filter_parameters_url))
        self.assertEquals(response.status_code, 200)

    def test_product_summary_GET(self):
        response = self.client.get(reverse(self.product_summary_url))
        self.assertEquals(response.status_code, 200)

    def test_equity_summary_GET(self):
        response = self.client.get(reverse(self.equity_summary_url))
        self.assertEquals(response.status_code, 200)

    def test_products_GET(self):
        response = self.client.get(reverse(self.products_url))
        self.assertEquals(response.status_code, 200)

    def test_filters_parameters_suppliers_GET(self):
        response = self.client.get(reverse(self.filters_parameters_suppliers_url))
        self.assertEquals(response.status_code, 200)

    def test_filters_parameters_buyers_GET(self):
        response = self.client.get(reverse(self.filters_parameters_buyers_url))
        self.assertEquals(response.status_code, 200)

    def test_filters_parameters_static_GET(self):
        response = self.client.get(reverse(self.filters_parameters_static_url))
        self.assertEquals(response.status_code, 200)

    def test_product_spending_comparison_GET(self):
        response = self.client.get(reverse(self.product_spending_comparison_url))
        self.assertEquals(response.status_code, 200)

    def test_buyer_trend_GET(self):
        response = self.client.get(reverse(self.buyer_trend_url))
        self.assertEquals(response.status_code, 200)

    def test_supplier_trend_GET(self):
        response = self.client.get(reverse(self.supplier_trend_url))
        self.assertEquals(response.status_code, 200)

    def test_direct_open_contract_trend_GET(self):
        response = self.client.get(reverse(self.direct_open_contract_trend_url))
        self.assertEquals(response.status_code, 200)

    def test_contract_red_flags_GET(self):
        response = self.client.get(reverse(self.contract_red_flags_url))
        self.assertEquals(response.status_code, 200)

    def test_red_flag_summary_GET(self):
        response = self.client.get(reverse(self.red_flag_summary_url))
        self.assertEquals(response.status_code, 200)
