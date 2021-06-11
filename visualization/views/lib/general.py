def add_filter_args(filter_type, filter_value, filter_args, append_only=False):
    if append_only and filter_type:
        filter_args[filter_type] = filter_value
        return filter_args

    if filter_value == "notnull":
        filter_args[f"{filter_type}__isnull"] = False
        return filter_args

    if filter_value != "notnull":
        filter_args[f"{filter_type}__id"] = filter_value

    return filter_args
