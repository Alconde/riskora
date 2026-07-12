from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()


@register.simple_tag(takes_context=True)
def is_active(context, url_name, exact=False):
    request = context.get('request')
    if not request:
        return ''

    try:
        url = reverse(url_name)
    except NoReverseMatch:
        return ''

    current_path = request.path

    if exact:
        return 'is-active' if current_path == url else ''

    return 'is-active' if current_path.startswith(url) else ''