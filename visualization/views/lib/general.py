def add_filter_args(filter_type, filter_value, filter_args):
    if filter_value != "notnull":
        filter_args[f"{filter_type}__id"] = filter_value
    else:
        filter_args[f"{filter_type}__isnull"] = False
    return filter_args
