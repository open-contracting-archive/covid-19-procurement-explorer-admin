from django.test import TestCase
from rest_framework import status


class CovidAdminViewTest(TestCase):
    def setUp(self):
        self.not_found_url = "404"

    def test_not_found_GET(self):
        url = "/api/v1/404"
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
