from django.conf import settings


def page_expire_period(page_name=None, default_period=settings.CACHES["default"]["EXPIRE_PERIOD"]):
    # DEBUG = True
    if settings.DEBUG:
        return 1

    # list page name it's expire value
    # {'page_name':1233}
    page_list = {}

    if page_name is None:
        return default_period

    if page_name:
        return page_list.get(page_name, default_period)
