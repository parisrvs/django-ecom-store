from .models import Order, Product, Category, Variation, Pincode, Tag
from datetime import datetime
from django.core.paginator import Paginator
from django.urls import reverse
from django.conf import settings
from django.db.models import Count, F, Value

def get_search_products(request):
    q = request.GET.get('q')
    if not q:
        return None
    products = Product.objects.filter(title__istartswith=q).values("id")
    tags = Tag.objects.prefetch_related("products").filter(name__istartswith=q)
    for tag in tags:
        products = products.union(tag.products.prefetch_related("variations").all())
    
    if not products:
        return {"products": None, "search_query": q}
    
    variations = Variation.objects.select_related("product").filter(product__in=products)
    variations = variations.select_related("discount").prefetch_related(
        "keyvalues",
        "images",
        "keyvalues__key",
        "keyvalues__value"
    ).filter(availability=True)

    selected_sort = None
    if request.GET.get('sort'):
        sort = request.GET.get('sort')
        if sort == "z-a":
            variations = variations.order_by("-product")
            selected_sort = {"value": sort, "display": "Z - A"}
        elif sort == "price-asc":
            variations = variations.order_by("price", "product")
            selected_sort = {"value": sort, "display": "Price (Low to High)"}
        elif sort == "price-desc":
            variations = variations.order_by("-price", "product")
            selected_sort = {"value": sort, "display": "Price (High to Low)"}
        else:
            selected_sort = {"value": "a-z", "display": "A - Z"}
        selected_sort["url"] = f"sort={sort}"
    else:
        variations = variations.prefetch_related("orderitems").annotate(
            num_orders=Count("orderitems")
        ).order_by("-num_orders", "price")
    
    if not variations:
        return {"products": None, "search_query": q}
    
    paginator = Paginator(variations, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return {"products": page_obj, "search_query": q, "search_filter_query": selected_sort}


def get_products(request):
    product = None
    filter_query = '?'
    categories = Category.objects.all()
    if request.GET.get('category'):
        products = Product.objects.filter(categories__slug=request.GET.get('category'))
        filter_query += f"category={request.GET.get('category')}&"
    else:
        products = Product.objects.all()
    if request.GET.get('product'):
        product = Product.objects.filter(slug=request.GET.get('product')).first()
        filter_query += f"product={request.GET.get('product')}&"
    
    if product:
        variations = product.variations.all()
    else:
        variations = Variation.objects.select_related("product").filter(product__in=products)
    variations = variations.select_related("discount").prefetch_related(
        "keyvalues",
        "images",
        "keyvalues__key",
        "keyvalues__value"
    ).filter(availability=True, inventory__gt=0)

    selected_sort = None
    if request.GET.get('sort'):
        sort = request.GET.get('sort')
        if sort == "z-a":
            variations = variations.order_by("-product")
            selected_sort = {"value": sort, "display": "Z - A"}
        elif sort == "price-asc":
            variations = variations.order_by("price", "product")
            selected_sort = {"value": sort, "display": "Price (Low to High)"}
        elif sort == "price-desc":
            variations = variations.order_by("-price", "product")
            selected_sort = {"value": sort, "display": "Price (High to Low)"}
        else:
            selected_sort = {"value": "a-z", "display": "A - Z"}
        filter_query += f"sort={sort}&"
    else:
        variations = variations.prefetch_related("orderitems").annotate(
            num_orders=Count("orderitems")
        ).order_by("-num_orders", "price")

    
    paginator = Paginator(variations, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if filter_query == '?':
        filter_query = None

    try:
        selected_category = None if not request.GET.get('category') else Category.objects.get(slug=request.GET.get('category'))
    except:
        selected_category = None
    selected_product = None if not request.GET.get('product') else product

    return {
        "products": page_obj,
        "selected_category": selected_category,
        "selected_product": selected_product,
        "selected_sort": selected_sort,
        "products_set": products,
        "categories": categories,
        "filter_query": filter_query
    }


def validate_email(emailaddress):
    pos_AT = 0
    count_AT = 0
    count_DT = 0
    if emailaddress[0] == '@' or emailaddress[-1] == '@':
        return False
    if emailaddress[0] == '.' or emailaddress[-1] == '.':
        return False
    for c in range(len(emailaddress)):
        if emailaddress[c] == '@':
            pos_AT = c
            count_AT = count_AT + 1
    if count_AT != 1:
        return False
        
    username = emailaddress[0:pos_AT]
    if not username[0].isalnum() or not username[-1].isalnum():
        return False
    for d in range(len(emailaddress)):
        if emailaddress[d] == '.':
            if d == (pos_AT+1):
                return False
            if d > pos_AT:
                word = emailaddress[(pos_AT+1):d]
                if not word.isalnum():
                    return False
                pos_AT = d
                count_DT = count_DT + 1
    if count_DT < 1 or count_DT > 2:
        return False
        
    return True


### is this product available at this pincode
def check_availability(pincode, variation_id, variation_delivery_time_in_days):
    try:
        p = Pincode.objects.get(pincode=pincode)
    except:
        return {"availability": False}
    
    if Pincode.objects.filter(pincode=pincode, products_unavailable__id=variation_id).exists():
        return {"availability": False}
    
    if p.delivery_time_in_days > variation_delivery_time_in_days:
        return {"availability": True, "delivery_time_in_days": p.delivery_time_in_days}
    else:
        return {"availability": True, "delivery_time_in_days": variation_delivery_time_in_days}



def add_item_to_cart(request, variation_id, qty):
    try:
        qty = float(qty)
        variation_id = int(variation_id)
    except:
        return {"success": False}
    
    variation = Variation.objects.select_related("discount", "product").prefetch_related(
        "keyvalues",
        "keyvalues__key",
        "keyvalues__value"
    ).filter(id=variation_id, availability=True, inventory__gt=0).first()

    if variation.inventory < qty:
        return {"success": False, "out_of_stock": f"Available: {variation.inventory} {variation.unit}"}
    
    if not request.session.get("cart", False):
        request.session["cart"] = {
            "cart_items": {},
            "cart_amount": {
                "amount": 0,
                "discount": 0,
                "discount_code": None,
                "amount_payable": 0
            },
            "count": 0,
            "currency": settings.CURRENCY,
            "checkout_url": reverse('store:checkout'),
            "delivery_address": None
        }
    
    vid = str(variation_id)
    zipcode_availability = None
    unit_price = float(variation.price)
    amount = (qty * unit_price)
    amount_payable = amount
    discount = 0
    if variation.discount:
        amount_payable = amount - (amount*(variation.discount.percent/100))
        discount = variation.discount.percent
    
    if vid not in request.session["cart"]["cart_items"]:
        key_value_pair = []
        for kv in variation.keyvalues.all():
            key_value_pair.append({
                "key": kv.key.key.strip().lower().title(),
                "value": kv.value.value.strip().lower().title()
            })
        request.session["cart"]["cart_items"][vid] = {
            "title": variation.product.title.strip().lower().title(),
            "id": variation.id,
            "qty": round(qty, 2),
            "unit_price": round(unit_price, 2),
            "unit": variation.unit,
            "amount": round(amount, 2),
            "discount": discount,
            "amount_payable": round(amount_payable, 2),
            "key_value_pair": key_value_pair,
            "currency": settings.CURRENCY,
            "zipcode_availability": zipcode_availability,
            "delivery_time_in_days": variation.delivery_time_in_days
        }
    else:
        request.session["cart"]["cart_items"][vid]["qty"] = round((request.session["cart"]["cart_items"][vid]["qty"] + qty), 2)
        request.session["cart"]["cart_items"][vid]["amount"] = round((request.session["cart"]["cart_items"][vid]["amount"] + amount), 2)
        request.session["cart"]["cart_items"][vid]["amount_payable"] = round((request.session["cart"]["cart_items"][vid]["amount_payable"] + amount_payable), 2)
        
    if request.session["cart"]["delivery_address"] and settings.CHECK_DELIVERABILITY:
        request.session["cart"]["cart_items"][vid]["zipcode_availability"] = check_availability(
            request.session["cart"]["delivery_address"]["pincode"],
            variation_id,
            request.session["cart"]["cart_items"][vid]["delivery_time_in_days"]
        )

    request.session["cart"]["cart_amount"]["amount"] = round((request.session["cart"]["cart_amount"]["amount"] + amount_payable), 2)
    if request.session["cart"]["cart_amount"]["discount"]:
        d = request.session["cart"]["cart_amount"]["discount"]
        amount_payable = amount_payable - (amount_payable*(d/100))
    request.session["cart"]["cart_amount"]["amount_payable"] = round((request.session["cart"]["cart_amount"]["amount_payable"] + amount_payable), 2)
    request.session["cart"]["count"] = len(request.session["cart"]["cart_items"].keys())
    request.session.modified = True
    return {"success": True, "count": request.session["cart"]["count"]}


def remove_item_from_cart(request, variation_id):
    try:
        variation_id = int(variation_id)
    except ValueError:
        return {"success": False, "message": "Invalid Request"}
    
    if not Variation.objects.filter(id=variation_id).exists():
        return {"success": False, "message": "Invalid Request"}
    
    vid = str(variation_id)
    if vid not in request.session["cart"]["cart_items"]:
        return {"success": False, "message": "Invalid Request"}
    
    item_amount_payable = request.session["cart"]["cart_items"][vid]["amount_payable"]
    cart_amount = request.session["cart"]["cart_amount"]["amount"]
    cart_amount_payable = request.session["cart"]["cart_amount"]["amount_payable"]
    request.session["cart"]["cart_items"].pop(vid)

    request.session["cart"]["cart_amount"]["amount"] = round((cart_amount - item_amount_payable), 2)
    if request.session["cart"]["cart_amount"]["discount"]:
        d = request.session["cart"]["cart_amount"]["discount"]
        item_amount_payable = item_amount_payable - (item_amount_payable*(d/100))
    request.session["cart"]["cart_amount"]["amount_payable"] = round((cart_amount_payable - item_amount_payable), 2)
    request.session["cart"]["count"] = len(request.session["cart"]["cart_items"].keys())
    if request.session["cart"]["count"] == 0:
        request.session["cart"].clear()
        request.session.pop("cart", False)
        request.session.modified = True
        return {"success": True, "cart": False, "count": 0}
    request.session.modified = True
    return {"success": True, "count": request.session["cart"]["count"], "cart": request.session["cart"]}


def get_preferred_delivery_time(pdt):
    # Fri, 23 Sep 2022 00:00:00 GMT
    f = "%a, %d %b %Y %H:%M:%S %Z"
    try:
        dt = datetime.strptime(pdt, f)
    except:
        dt = None
    return dt


def deliveverable_at_location(request, pincode):
    if not Pincode.objects.filter(pincode=pincode).exists():
        return {"availability": False, "deliverability": False}
    
    for item in request.session["cart"]["cart_items"].values():
        if not item["zipcode_availability"]["availability"]:
            return {"availability": False, "deliverability": True}
    
    return {"availability": True, "deliverability": True}


def max_delivery_time(request, pincode):
    p = []
    pin = Pincode.objects.filter(pincode=pincode).first()
    if pin and settings.CHECK_DELIVERABILITY:
        p.append(pin.delivery_time_in_days)
    
    for item in request.session["cart"]["cart_items"].values():
        p.append(item["delivery_time_in_days"])
    return max(p)


def get_all_orders(request):
    orders = Order.objects.select_related("address", "discount", "cancellation").filter(customer=request.user)
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def check_inventory(items):
    for item in items:
        v = Variation.objects.filter(id=item["id"]).first()
        if v and v.inventory < item["qty"]:
            if v.inventory <= 0:
                return {"success": False, "message": f"{item['title']} (ID: {v.id}) is out of stock."}
            return {"success": False, "message": f"Only {v.inventory} {v.unit} of {item['title']} (ID: {v.id}) is available."}
    return {"success": True}
