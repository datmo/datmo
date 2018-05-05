#!/usr/bin/python

try:
    to_unicode = unicode
except NameError:
    to_unicode = str
from datmo.core.util.lang import get_lang

MESSAGES = get_lang()


def get(message_type, key, values=None):
    if isinstance(values, dict) and len(values) > 0:
        return MESSAGES[message_type][key].format(*values, **values)
    elif isinstance(values, str) or isinstance(values, to_unicode):
        return MESSAGES[message_type][key] % str(values)
    elif isinstance(values, tuple):
        return MESSAGES[message_type][key] % values
    else:
        return MESSAGES[message_type][key]
