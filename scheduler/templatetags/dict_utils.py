# timetable_project/scheduler/templatetags/dict_utils.py
from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """
    Safe dict lookup in templates:  {{ mydict|dict_get:var }}
    Works for int keys and string keys.
    """
    if d is None:
        return None
    # Try direct dict .get
    try:
        val = d.get(key)
        if val is not None:
            return val
    except Exception:
        pass
    # Try string key
    try:
        return d.get(str(key))
    except Exception:
        pass
    # fallback: try indexing
    try:
        return d[key]
    except Exception:
        pass
    return None


@register.filter
def to(start, end):
    """
    Generate a numeric range (inclusive) usable in Django templates.
    Example: {% for i in 1|to:5 %} -> 1,2,3,4,5
    """
    try:
        start, end = int(start), int(end)
        return range(start, end + 1)
    except Exception:
        return []
