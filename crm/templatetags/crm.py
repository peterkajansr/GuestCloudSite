from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def user_url(context, url_name, **kwargs):
    kwargs.setdefault('username', context['user'].username)
    return reverse(url_name, kwargs=kwargs) 