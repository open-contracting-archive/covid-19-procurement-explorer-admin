from django.urls import include, path
from rest_framework import routers
from . import views

urlpatterns = [
    path('total_contracts/', views.TotalContractsView.as_view()),
    path('total_spending/', views.TotalSpendingsView.as_view()),
    path('average_bids/', views.AverageBidsView.as_view()),
    path('global_overview/',views.GlobalOverView.as_view()),
    path('top_suppliers/',views.TopSuppliers.as_view()),
    path('top_buyers/',views.TopBuyers.as_view()),
    path('direct_open/',views.DirectOpen.as_view()),
    path('contract_status/',views.ContractStatusView.as_view())
]