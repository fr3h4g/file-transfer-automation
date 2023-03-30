"""Common functions."""
import re


def compare_filter(value: str | None, filter_value: str | None) -> bool:
    """Filter for filename in tasks."""
    if not value:
        value = ""
    if not filter_value:
        filter_value = ""
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
