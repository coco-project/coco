from ipynbsrv import settings
import json


def api_error_message(exception, params):
    if settings.DEBUG:
        return "{}. Data: {}".format(exception, json.dumps(params))
    else:
        return "Whooops, something went wrong when calling the API :("
