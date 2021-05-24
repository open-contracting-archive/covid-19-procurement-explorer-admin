from django.test import SimpleTestCase
from django.urls import resolve, reverse

from visualization.views import (
    AverageBidsView,
    BuyerProfileView,
    BuyerSummaryView,
    BuyerTrendView,
    ContractRedFlagsView,
    ContractStatusView,
    CountryMapView,
    CountryPartnerView,
    CountrySuppliersView,
    DataProviderView,
    DirectOpen,
    DirectOpenContractTrendView,
    EquityIndicatorView,
    EquitySummaryView,
    FilterParametersBuyers,
    FilterParametersStatic,
    FilterParametersSuppliers,
    FilterParams,
    GlobalOverView,
    GlobalSuppliersView,
    InsightsView,
    MonopolizationView,
    ProductDistributionView,
    ProductFlowView,
    ProductSpendingComparison,
    ProductSummaryView,
    ProductTableView,
    ProductTimelineRaceView,
    ProductTimelineView,
    QuantityCorrelation,
    RedFlagSummaryView,
    SupplierFlowView,
    SupplierProfileView,
    SupplierSummaryView,
    SupplierTrendView,
    TopBuyers,
    TopSuppliers,
    TotalContractsView,
    TotalSpendingView,
    WorldMapView,
)


class TestUrls(SimpleTestCase):
    def test_total_contracts_url_is_resolved(self):
        url = reverse("total_contracts")
        self.assertEquals(resolve(url).func.view_class, TotalContractsView)

    def test_total_spending_url_is_resolved(self):
        url = reverse("total_spending")
        self.assertEquals(resolve(url).func.view_class, TotalSpendingView)

    def test_average_bids_url_is_resolved(self):
        url = reverse("average_bids")
        self.assertEquals(resolve(url).func.view_class, AverageBidsView)

    def test_world_map_race_url_is_resolved(self):
        url = reverse("world_map_race")
        self.assertEquals(resolve(url).func.view_class, GlobalOverView)

    def test_top_suppliers_url_is_resolved(self):
        url = reverse("top_suppliers")
        self.assertEquals(resolve(url).func.view_class, TopSuppliers)

    def test_top_buyers_url_is_resolved(self):
        url = reverse("top_buyers")
        self.assertEquals(resolve(url).func.view_class, TopBuyers)

    def test_direct_open_url_is_resolved(self):
        url = reverse("direct_open")
        self.assertEquals(resolve(url).func.view_class, DirectOpen)

    def test_contract_status_url_is_resolved(self):
        url = reverse("contract_status")
        self.assertEquals(resolve(url).func.view_class, ContractStatusView)

    def test_quantity_correlation_url_is_resolved(self):
        url = reverse("quantity_correlation")
        self.assertEquals(resolve(url).func.view_class, QuantityCorrelation)

    def test_monopolization_url_is_resolved(self):
        url = reverse("monopolization")
        self.assertEquals(resolve(url).func.view_class, MonopolizationView)

    def test_country_suppliers_url_is_resolved(self):
        url = reverse("country_suppliers")
        self.assertEquals(resolve(url).func.view_class, CountrySuppliersView)

    def test_country_map_url_is_resolved(self):
        url = reverse("country_map")
        self.assertEquals(resolve(url).func.view_class, CountryMapView)

    def test_world_map_url_is_resolved(self):
        url = reverse("world_map")
        self.assertEquals(resolve(url).func.view_class, WorldMapView)

    def test_country_map_api_url_is_resolved(self):
        url = reverse("country_map_api")
        self.assertEquals(resolve(url).func.view_class, CountryMapView)

    def test_global_suppliers_url_is_resolved(self):
        url = reverse("global_suppliers")
        self.assertEquals(resolve(url).func.view_class, GlobalSuppliersView)

    def test_product_distribution_url_is_resolved(self):
        url = reverse("product_distribution")
        self.assertEquals(resolve(url).func.view_class, ProductDistributionView)

    def test_equity_indicators_url_is_resolved(self):
        url = reverse("equity_indicators")
        self.assertEquals(resolve(url).func.view_class, EquityIndicatorView)

    def test_product_timeline_url_is_resolved(self):
        url = reverse("product_timeline")
        self.assertEquals(resolve(url).func.view_class, ProductTimelineView)

    def test_product_timeline_race_url_is_resolved(self):
        url = reverse("product_timeline_race")
        self.assertEquals(resolve(url).func.view_class, ProductTimelineRaceView)

    def test_country_partners_url_is_resolved(self):
        url = reverse("country_partners")
        self.assertEquals(resolve(url).func.view_class, CountryPartnerView)

    def test_data_providers_url_is_resolved(self):
        url = reverse("data_providers")
        self.assertEquals(resolve(url).func.view_class, DataProviderView)

    def test_buyer_summary_url_is_resolved(self):
        url = reverse("buyer_summary")
        self.assertEquals(resolve(url).func.view_class, BuyerSummaryView)

    def test_supplier_summary_url_is_resolved(self):
        url = reverse("supplier_summary")
        self.assertEquals(resolve(url).func.view_class, SupplierSummaryView)

    def test_filter_parameters_url_is_resolved(self):
        url = reverse("filter_parameters")
        self.assertEquals(resolve(url).func.view_class, FilterParams)

    def test_product_summary_url_is_resolved(self):
        url = reverse("product_summary")
        self.assertEquals(resolve(url).func.view_class, ProductSummaryView)

    def test_equity_summary_url_is_resolved(self):
        url = reverse("equity_summary")
        self.assertEquals(resolve(url).func.view_class, EquitySummaryView)

    def test_products_url_is_resolved(self):
        url = reverse("products")
        self.assertEquals(resolve(url).func.view_class, ProductTableView)

    def test_filters_parameters_suppliers_url_is_resolved(self):
        url = reverse("filters_parameters_suppliers")
        self.assertEquals(resolve(url).func.view_class, FilterParametersSuppliers)

    def test_filters_parameters_buyers_url_is_resolved(self):
        url = reverse("filters_parameters_buyers")
        self.assertEquals(resolve(url).func.view_class, FilterParametersBuyers)

    def test_filters_parameters_static_url_is_resolved(self):
        url = reverse("filters_parameters_static")
        self.assertEquals(resolve(url).func.view_class, FilterParametersStatic)

    def test_product_spending_comparison_url_is_resolved(self):
        url = reverse("product_spending_comparison")
        self.assertEquals(resolve(url).func.view_class, ProductSpendingComparison)

    def test_buyer_trend_url_is_resolved(self):
        url = reverse("buyer_trend")
        self.assertEquals(resolve(url).func.view_class, BuyerTrendView)

    def test_supplier_trend_url_is_resolved(self):
        url = reverse("supplier_trend")
        self.assertEquals(resolve(url).func.view_class, SupplierTrendView)

    def test_direct_open_contract_trend_url_is_resolved(self):
        url = reverse("direct_open_contract_trend")
        self.assertEquals(resolve(url).func.view_class, DirectOpenContractTrendView)

    def test_contract_red_flags_url_is_resolved(self):
        url = reverse("contract_red_flags")
        self.assertEquals(resolve(url).func.view_class, ContractRedFlagsView)

    def test_red_flag_summary_url_is_resolved(self):
        url = reverse("red_flag_summary")
        self.assertEquals(resolve(url).func.view_class, RedFlagSummaryView)

    def test_supplier_detail_url_is_resolved(self):
        url = reverse("supplier_detail", args=["1"])
        self.assertEquals(resolve(url).func.view_class, SupplierProfileView)

    def test_buyer_detail_url_is_resolved(self):
        url = reverse("buyer_detail", args=["1"])
        self.assertEquals(resolve(url).func.view_class, BuyerProfileView)

    def test_product_flow_view_url_is_resolved(self):
        url = reverse("product_flow_view", args=["1"])
        self.assertEquals(resolve(url).func.view_class, ProductFlowView)

    def test_supplier_flow_view_url_is_resolved(self):
        url = reverse("supplier_flow_view", args=["1"])
        self.assertEquals(resolve(url).func.view_class, SupplierFlowView)

    def test_insights_view_url_is_resolved(self):
        url = reverse("insights_view")
        self.assertEquals(resolve(url).func.view_class, InsightsView)
