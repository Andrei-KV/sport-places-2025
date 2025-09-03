from django import template

register = template.Library()

@register.filter
def pluralize_places(value):
    """
    Склоняет слово  в зависимости от числа.
    """
    if value is None:
        return '0 мест'
        
    last_digit = value % 10
    last_two_digits = value % 100

    if last_two_digits in [11, 12, 13, 14]:
        return f"{value} мест"
    elif last_digit == 1:
        return f"{value} место"
    elif last_digit in [2, 3, 4]:
        return f"{value} места"
    else:
        return f"{value} мест"