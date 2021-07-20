from django.conf import settings
from django.test import SimpleTestCase
from django.test.utils import override_settings

from helpers.general import page_expire_period
from visualization.views.lib.general import add_filter_args


class TestGeneral(SimpleTestCase):
    @override_settings(DEBUG=False)
    def test_page_expire_period(self):
        default_timeout = settings.CACHES["default"]["EXPIRE_PERIOD"]
        time = page_expire_period()
        self.assertEquals(time, default_timeout)

    @override_settings(DEBUG=False)
    def test_page_expire_period_specific_page(self):
        default_timeout = settings.CACHES["default"]["EXPIRE_PERIOD"]
        time = page_expire_period("sample_page")
        self.assertEquals(time, default_timeout)

    def test_add_filter_args(self):
        result = add_filter_args("foo", "bar", {})
        self.assertEquals(result, {"foo__id": "bar"})

    def test_add_filter_args_notnull(self):
        result = add_filter_args("foo", "notnull", {})
        self.assertEquals(result, {"foo__isnull": False})

    def test_add_filter_args_append_only(self):
        result = add_filter_args("foo", "bar", {}, append_only=True)
        self.assertEquals(result, {"foo": "bar"})
