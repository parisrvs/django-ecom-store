from django import template

register = template.Library()

@register.filter(name='calculate_discount')
def calculate_discount(price, percent=None):
    try:
        price = round(float(price), 2)
        percent = int(percent)
    except:
        return price
    
    discounted_price = price - (price*(percent/100))
    return round(discounted_price, 2)
