from past.builtins import basestring
from datmo.util.lang import get_lang

MESSAGES = get_lang()

def get(key, values=None):
    if isinstance(values, dict) and len(values) > 0:
        return MESSAGES[key].format(*values, **values)
    elif isinstance(values, basestring):
        return MESSAGES[key] % str(values)
    elif isinstance(values, tuple):
        return MESSAGES[key] % values
    else:
        return MESSAGES[key]
