from django import template

register = template.Library()


@register.filter
def index(lst, i):
    if lst is str:
        return None
    idx = int(i)
    if idx in lst:
        return lst[idx]
    else:
        return None
