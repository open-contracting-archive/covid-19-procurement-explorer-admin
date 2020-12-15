from django.urls import include, path
from rest_framework import routers
from . import views

urlpatterns = [
    path('total-contracts/', views.TotalContractsView.as_view()),
    path('total-spending/', views.TotalSpendingsView.as_view()),
    path('average-bids/', views.AverageBidsView.as_view()),
    path('global-overview/',views.GlobalOverView.as_view()),
    path('top-suppliers/',views.TopSuppliers.as_view()),
    path('top-buyers/',views.TopBuyers.as_view()),
    path('direct-open/',views.DirectOpen.as_view()),
    path('contract-status/',views.ContractStatusView.as_view()),
    path('quantity-correlation/',views.QuantityCorrelation.as_view()),
]