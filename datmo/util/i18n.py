from past.builtins import basestring

from datmo.util.lang import get_lang

MESSAGES = get_lang()


def get(type, key, values=None):
    if isinstance(values, dict) and len(values) > 0:
        return MESSAGES[type][key].format(*values, **values)
    elif isinstance(values, basestring):
        return MESSAGES[type][key] % str(values)
    elif isinstance(values, tuple):
        return MESSAGES[type][key] % values
    else:
        return MESSAGES[type][key]
