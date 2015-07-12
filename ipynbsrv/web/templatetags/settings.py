from django import conf, template
from ipynbsrv.web import settings

register = template.Library()


@register.simple_tag
def settings(option):
    '''
    Templatetag function that allows views to access settings.

    Example:
        {% load settings %}
        {% settings 'STATIC_URL' %}
    '''
    value = getattr(settings, option, None)  # check module local settings first
    if value is None:
        value = getattr(conf.settings, option, '')
    return value
