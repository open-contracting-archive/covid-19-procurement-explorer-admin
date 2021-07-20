from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("api/v1/language", views.LanguageView)
router.register("api/v1/buyers", views.BuyerView, basename="BuyerView")
router.register("api/v1/suppliers", views.SupplierView, basename="SupplierView")
router.register("api/v1/contracts", views.TenderView, basename="TenderView")
router.register("api/v1/overall-stat-summary", views.OverallStatSummaryView, basename="OverallStatSummaryView")

urlpatterns = [
    path("", include(router.urls)),
    path("data-import/", views.DataImportView.as_view(), name="data_import"),
    path("data-validate/", views.DataValidateView.as_view(), name="data_validate"),
    path("data-edit/", views.DataEditView.as_view(), name="data_edit"),
    path("delete-dataset/", views.DeleteDataSetView.as_view(), name="data_delete"),
]
