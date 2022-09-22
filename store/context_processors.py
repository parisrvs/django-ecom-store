from django.conf import settings

def site_defaults(request):
    try:
        sitetitle = settings.SITE_TITLE
    except AttributeError:
        sitetitle = "blackparis"
    
    try:
        currency = settings.CURRENCY
    except AttributeError:
        currency = "Rs."
    
    if request.session.get("cart", False) and request.session["cart"].get("cart_items", False):
        count = len(request.session["cart"]["cart_items"].keys())
    else:
        count = 0

    context = {
        "sitetitle": sitetitle,
        "currency": currency,
        "cart_items_Count": count
    }
    return context