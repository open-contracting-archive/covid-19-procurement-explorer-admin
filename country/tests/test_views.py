from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class CountryViewTest(TestCase):
    def setUp(self):
        self.buyer_list_api_url = "BuyerView-list"
        self.country_list_api_url = "country-list"
        self.language_list_api_url = "language-list"
        self.supplier_list_api_url = "SupplierView-list"
        self.tender_list_api_url = "TenderView-list"
        self.overview_summary_list_api_url = "OverallStatSummaryView-list"
        self.country_choices_api_url = "country-choices"
        self.data_edit_url = "data_edits"
        self.data_imports_url = "data_imports"
        self.data_validate_url = "data_validate"
        self.data_delete_url = "data_delete"

    def test_buyer_list_GET(self):
        url = "%s?country=KE&buyer_name=buyer2&product=1" % reverse(self.buyer_list_api_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_country_list_GET(self):
        url = reverse(self.country_list_api_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_country_choice_list_GET(self):
        url = reverse(self.country_choices_api_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_language_list_GET(self):
        url = reverse(self.country_list_api_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_supplier_list_GET(self):
        url = "%s?country=KE&supplier_name=supplier&product=1" % reverse(self.supplier_list_api_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_tender_list_GET(self):
        url_string = "%s?&country=1&buyer=1&supplier=1&product=1&status=open&procurement_procedure=direct&title=title"
        url_string += (
            "&date_from=2020-01-01&date_to=2021-01-01&contract_value_usd=112&value_comparison=true&equity_id=1"
        )
        url = url_string % reverse(self.tender_list_api_url)

        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_overview_summary_list_GET(self):
        url = reverse(self.overview_summary_list_api_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_data_edit_GET(self):
        url = "%s?data_import_id=1" % reverse(self.data_edit_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)

    def test_data_imports_GET(self):
        url = "%s?country=1&data_import_id=1&validated=true" % reverse(self.data_imports_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)

    def test_data_imports_without_validate_GET(self):
        url = "%s?country=1&data_import_id=1" % reverse(self.data_imports_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)

    def test_data_validate_GET(self):
        url = "%s?data_import_id=1" % reverse(self.data_validate_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)

    def test_data_validate_without_import_id_GET(self):
        url = reverse(self.data_validate_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)

    def test_data_delete_GET(self):
        url = "%s?data_import_id=1" % reverse(self.data_delete_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)

    def test_data_delete_without_id_GET(self):
        url = reverse(self.data_delete_url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
