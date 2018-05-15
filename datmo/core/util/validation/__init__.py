import os
import yaml
from cerberus import Validator
from cerberus.schema import SchemaError
from datmo.core.util.exceptions import ValidationFailed, ValidationSchemaMissing

# http://docs.python-cerberus.org/en/stable/usage.html

schema_yaml = open(os.path.join(os.path.split(__file__)[0], "schemas.yml"))

schemas = yaml.safe_load(schema_yaml)


def validate(schema_name, values):
    try:
        v = Validator(schemas.get(schema_name))
        response = v.validate(values)

        if response == False:
            raise ValidationFailed(v.errors)
        return True
    except SchemaError:
        raise ValidationSchemaMissing(schema_name)
