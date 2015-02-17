from django import template
from django import conf


register = template.Library()


"""
Templatetag function that allows views to access app settings.

Example:
    {% load settings %}
    {% settings 'PUBLIC_URL' %}
"""
@register.simple_tag
def settings(name):
    return getattr(conf.settings, name, '')
