import jsonschema
from jsonschema import validate

def validate_json(instance, schema):
    try:
        validate(instance=instance, schema=schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e)
