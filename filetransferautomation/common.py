import re


def compare_filter(value: str, filter_value: str) -> bool:
    value = value.strip()
    filter_value_regex = filter_value.strip()
    filter_value_regex = "^" + filter_value_regex + "$"
    filter_value_regex = filter_value_regex.replace("\\", "\\\\")
    filter_value_regex = filter_value_regex.replace(".", "\\.{0,1}")
    filter_value_regex = filter_value_regex.replace("*", ".*")
    filter_value_regex = filter_value_regex.replace("?", ".")
    if re.findall(filter_value_regex, value, flags=re.IGNORECASE):
        return True
    return False
