from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('api/v1/country', views.CountryView)
router.register('api/v1/language', views.LanguageView)
router.register('api/v1/tender', views.TenderView)

urlpatterns = [
    path('', include(router.urls))
]
