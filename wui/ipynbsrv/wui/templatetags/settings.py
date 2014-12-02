from django import template
from django import conf


register = template.Library()

""
@register.simple_tag
def settings(name):
    return getattr(conf.settings, name, "")
