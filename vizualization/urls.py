from django.urls import include, path
from rest_framework import routers
from . import views

urlpatterns = [
    path('total-contracts/', views.TotalContractsView.as_view()),
    path('total-spending/', views.TotalSpendingsView.as_view()),
    path('average-bids/', views.AverageBidsView.as_view()),
    path('world-map-race/',views.GlobalOverView.as_view()),
    path('top-suppliers/',views.TopSuppliers.as_view()),
    path('top-buyers/',views.TopBuyers.as_view()),
    path('direct-open/',views.DirectOpen.as_view()),
    path('contract-status/',views.ContractStatusView.as_view()),
    path('quantity-correlation/',views.QuantityCorrelation.as_view()),
    path('monopolization/',views.MonopolizationView.as_view()),
    path('country-suppliers/',views.CountrySuppliersView.as_view()),
    path('country-map/',views.CountryMapView.as_view()),
    path('world-map/',views.WorldMapView.as_view()),
    path('country-map-api/',views.CountryMapView.as_view()),
    path('global-suppliers/',views.GlobalSuppliersView.as_view()),
    path('product-distribution/',views.ProductDistributionView.as_view()),
    path('equity-indicators/',views.EquityIndicatorView.as_view()),
    path('product-timeline/',views.ProductTimelineView.as_view()),
    path('product-timeline-race/',views.ProductTimelineRaceView.as_view()),
    path('suppliers/<int:pk>',views.SupplierProfileView.as_view()),
    path('buyers/<int:pk>',views.BuyerProfileView.as_view()),
    path('country-partners/',views.CountryPartnerView.as_view()),
    path('buyer-summary/',views.BuyerSummaryView.as_view()),
    path('supplier-summary/',views.SupplierSummaryView.as_view()),
    path('filter-parameters/',views.FilterParams.as_view()),
    path('product-summary/',views.ProductSummaryView.as_view()),
    path('equity-summary/',views.EquitySummaryView.as_view()),
] 
