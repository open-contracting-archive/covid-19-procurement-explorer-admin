from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('api/v1/country', views.CountryView)
router.register('api/v1/language', views.LanguageView)
router.register('api/v1/buyers', views.BuyerView,basename='BuyerView')
router.register('api/v1/suppliers', views.SupplierView,basename='SupplierView')
router.register('api/v1/contracts', views.TenderView,basename='TenderView')

urlpatterns = [
    path('', include(router.urls))
]
