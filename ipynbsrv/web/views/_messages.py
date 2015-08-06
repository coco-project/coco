from ipynbsrv import settings


def api_error_message(exception, params):
    if settings.DEBUG:
        return "{}. Data: {}".format(exception, params)
    else:
        return "Whooops, something went wrong when calling the API :("