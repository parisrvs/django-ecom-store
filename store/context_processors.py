from .models import Category
from django.conf import settings

def site_defaults(request):
    categories = Category.objects.all()
    try:
        sitetitle = settings.SITE_TITLE
    except AttributeError:
        sitetitle = "blackparis"
    
    try:
        currency = settings.CURRENCY
    except AttributeError:
        currency = "Rs."
    
    try:
        delivery_time_hours = settings.DELIVERY_TIME_IN_HOURS
    except AttributeError:
        delivery_time_hours = 24
    
    try:
        delivery_time_days = settings.DELIVERY_TIME_IN_DAYS
    except AttributeError:
        delivery_time_days = 1
    
    if request.session.get("cart", False) and request.session["cart"].get("cart_items", False):
        count = len(request.session["cart"]["cart_items"].keys())
    else:
        count = 0

    context = {
        "categories": categories,
        "sitetitle": sitetitle,
        "currency": currency,
        "cartItemsCount": count,
        "delivery_time_hours": delivery_time_hours,
        "delivery_time_days": delivery_time_days
    }
    return context