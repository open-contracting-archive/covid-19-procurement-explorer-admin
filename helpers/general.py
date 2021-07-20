import re

import inflect
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


def get_singular(value):
    p = inflect.engine()
    strings = value.split(" ")
    new_string_array = []
    for string in strings:
        singular = p.singular_noun(string)
        if not singular:
            new_string_array.append(string)
        else:
            new_string_array.append(singular)
    final_string = " ".join(new_string_array).title()
    return final_string


def close_string_mapping(value):
    my_new_string = re.sub("[^a-zA-Z0-9 \n\\.]", "", value.strip().lower())
    return get_singular(my_new_string)
