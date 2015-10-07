from django.core.exceptions import ValidationError
import json


def validate_json_format(data):
    """
    Validate that `data` is valid JSON format.
    """
    try:
        json.loads(data)
    except ValueError:
        raise ValidationError('"%s" is not valid JSON.' % data)
