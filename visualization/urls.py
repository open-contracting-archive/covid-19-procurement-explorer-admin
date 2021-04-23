from django.urls import path

from . import views

urlpatterns = [
    path("total-contracts/", views.TotalContractsView.as_view(), name="total_contracts"),
    path("total-spending/", views.TotalSpendingsView.as_view(), name="total_spending"),
    path("average-bids/", views.AverageBidsView.as_view(), name="average_bids"),
    path("world-map-race/", views.GlobalOverView.as_view(), name="world_map_race"),
    path("top-suppliers/", views.TopSuppliers.as_view(), name="top_suppliers"),
    path("top-buyers/", views.TopBuyers.as_view(), name="top_buyers"),
    path("direct-open/", views.DirectOpen.as_view(), name="direct_open"),
    path("contract-status/", views.ContractStatusView.as_view(), name="contract_status"),
    path("quantity-correlation/", views.QuantityCorrelation.as_view(), name="quantity_correlation"),
    path("monopolization/", views.MonopolizationView.as_view(), name="monopolization"),
    path("country-suppliers/", views.CountrySuppliersView.as_view(), name="country_suppliers"),
    path("country-map/", views.CountryMapView.as_view(), name="country_map"),
    path("world-map/", views.WorldMapView.as_view(), name="world_map"),
    path("country-map-api/", views.CountryMapView.as_view(), name="country_map_api"),
    path("global-suppliers/", views.GlobalSuppliersView.as_view(), name="global_suppliers"),
    path("product-distribution/", views.ProductDistributionView.as_view(), name="product_distribution"),
    path("equity-indicators/", views.EquityIndicatorView.as_view(), name="equity_indicators"),
    path("product-timeline/", views.ProductTimelineView.as_view(), name="product_timeline"),
    path("product-timeline-race/", views.ProductTimelineRaceView.as_view(), name="product_timeline_race"),
    path("suppliers/<int:pk>", views.SupplierProfileView.as_view()),
    path("buyers/<int:pk>", views.BuyerProfileView.as_view()),
    path("country-partners/", views.CountryPartnerView.as_view(), name="country_partners"),
    path("data-providers/", views.DataProviderView.as_view(), name="data_providers"),
    path("buyer-summary/", views.BuyerSummaryView.as_view(), name="buyer_summary"),
    path("supplier-summary/", views.SupplierSummaryView.as_view(), name="supplier_summary"),
    path("filter-parameters/", views.FilterParams.as_view(), name="filter_parameters"),
    path("product-summary/", views.ProductSummaryView.as_view(), name="product_summary"),
    path("equity-summary/", views.EquitySummaryView.as_view(), name="equity_summary"),
    path("products/", views.ProductTableView.as_view(), name="products"),
    path(
        "filters-parameters/suppliers/", views.FilterParametersSuppliers.as_view(), name="filters_parameters_suppliers"
    ),
    path("filters-parameters/buyers/", views.FilterParametersBuyers.as_view(), name="filters_parameters_buyers"),
    path("filters-parameters/static/", views.FilterParametersStatic.as_view(), name="filters_parameters_static"),
    path(
        "product-spending-comparison/", views.ProductSpendingComparison.as_view(), name="product_spending_comparison"
    ),
    path("buyer-trend/", views.BuyerTrendView.as_view(), name="buyer_trend"),
    path("supplier-trend/", views.SupplierTrendView.as_view(), name="supplier_trend"),
    path(
        "direct-open-contract-trend/", views.DirectOpenContractTrendView.as_view(), name="direct_open_contract_trend"
    ),
    path("contract-red-flags/", views.ContractRedFlagsView.as_view(), name="contract_red_flags"),
    path("red-flag-summary/", views.RedFlagSummaryView.as_view(), name="red_flag_summary"),
]
