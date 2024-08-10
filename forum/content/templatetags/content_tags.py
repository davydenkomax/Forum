from django import template
from datetime import time
import datetime

register = template.Library()

@register.filter
def mod(value, arg):
    try:
        return value % arg
    except (ValueError, ZeroDivisionError):
        return None
    