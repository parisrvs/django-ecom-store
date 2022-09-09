from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import IntegrityError, transaction
from time import sleep
from datetime import datetime, timezone
import math

from store.models import Discount, Product, Variation, Order, OrderItem, OrderCancellation
from authentication.models import Address
from . import database
from .pagination import get_products, get_orders, get_search_products
from .utility import validate_email, get_order_details


@ensure_csrf_cookie
def homepage(request, category_slug=None):
    products = get_products(request, category_slug)
    if products == None:
        return HttpResponseRedirect(reverse("store:homepage"))
    return render(
        request,
        "store/homepage.html",
        {"products": products}
    )


def product(request, product_slug):
    try:
        product_detail = Product.objects.prefetch_related(
            "images",
            "categories",
            "variations",
            "variations__keyvalues",
            "variations__keyvalues__key",
            "variations__keyvalues__value",
        ).get(slug=product_slug)
    except:
        return HttpResponseRedirect(reverse("store:homepage"))
    
    keys = set()
    variations = product_detail.variations.all()
    for variation in variations:
        for kvs in variation.keyvalues.all():
            keys.add(kvs.key.key)
    
    return render(
        request,
        "store/product.html",
        {"product": product_detail, "keys": keys}
    )


def variation(request, product_slug, variation_id):
    try:
        variation = Variation.objects.select_related("product").prefetch_related("keyvalues", "images", "keyvalues__key", "keyvalues__value").get(id=variation_id)
    except:
        return HttpResponseRedirect(reverse("store:homepage"))
    return render(
        request,
        "store/variation.html",
        {"variation": variation}
    )


def get_variations(request):
    if request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    product_id = request.POST["product_id"]
    if not product_id:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        product_id = int(product_id)
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        product = Product.objects.get(id=product_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        currency = settings.CURRENCY
    except AttributeError:
        currency = "Rs."
    
    variations = product.variations.prefetch_related("keyvalues", "images").all()
    v = []
    for variation in variations:
        if variation.availability and variation.inventory >= 1:
            i = []
            images = variation.images.all()[1:]
            for image in images:
                i.append({
                    "image": image.image.url,
                    "name": image.name
                })
            
            k_v = []
            keyvalues = variation.keyvalues.select_related("key", "value").all()
            for kv in keyvalues:
                k_v.append({
                    "key": kv.key.key.strip().lower().title(),
                    "value": kv.value.value.strip().lower().title()
                })
            
            v.append({
                "id": variation.id,
                "title": product.title.strip().lower().title(),
                "variation_url": reverse("store:variation", kwargs={"product_slug": product.slug, "variation_id": variation.id}),
                "price": round(float(variation.price), 2),
                "currency": currency,
                "unit": variation.unit.strip().lower().title(),
                "short_info": ((variation.info)[:200] + "..."),
                "info": variation.info,
                "keyvalues": k_v,
                "first_image_url": variation.images.first().image.url,
                "first_image_name": variation.images.first().name,
                "all_images": i,
            })
    return JsonResponse({"success": True, "variations": v, "product_name": product.title.strip().lower().title()})


def add2cart(request):
    if request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    var_id = request.POST["var_id"]
    qty = request.POST["qty"]

    if not var_id or not qty:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        var_id = int(var_id)
        qty = float(qty)
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if qty <= 0 or not Variation.objects.filter(id=var_id).exists():
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if not request.session.get("cart", False):
        request.session["cart"] = {"cart_items": {}}
        request.session.modified = True
    
    varid = str(var_id)
    if varid not in request.session["cart"]["cart_items"]:
        request.session["cart"]["cart_items"][varid] = qty
    else:
        request.session["cart"]["cart_items"][varid] += qty
    request.session.modified = True

    count = len(request.session["cart"]["cart_items"].keys())
    return JsonResponse({"success": True, "count": count})


def getCart(request):
    if not request.session.get("cart", False) or not request.session["cart"].get("cart_items", False):
        return JsonResponse({"success": False})
    cart = request.session["cart"]["cart_items"]

    try:
        currency = settings.CURRENCY
    except AttributeError:
        currency = "Rs."

    items = []
    total = 0
    for vid, qty in cart.items():
        try:
            vid = int(vid)
            v = Variation.objects.select_related("product").get(id=vid)
        except:
            pass
        else:
            k_v = []
            keyvalues = v.keyvalues.select_related("key", "value").all()
            for kv in keyvalues:
                k_v.append({
                    "key": kv.key.key.strip().lower().title(),
                    "value": kv.value.value.strip().lower().title()
                })
            
            price = float(v.price)
            amount = math.ceil(qty*price)
            items.append({
                "id": v.id,
                "price": round(float(v.price), 2),
                "title": v.product.title.strip().lower().title(),
                "variation_url": reverse("store:variation", kwargs={"product_slug": v.product.slug, "variation_id": v.id}),
                "unit": v.unit.strip().lower().title(),
                "keyvalues": k_v,
                "qty": qty,
                "amount": amount,
                "currency": currency
            })
            total += amount
    
    discount = False
    request.session["cart"]["cart_amount"] = total
    request.session.modified = True
    if request.session["cart"].get("cart_discount", False):
        dp = request.session["cart"]["cart_discount"]["percent"]
        discounted_amount = math.floor((float(total*dp))/100)
        amount_payable = total - discounted_amount
        if request.session["cart"]["cart_discount"]["discounted_amount"] != discounted_amount:
            request.session["cart"]["cart_discount"]["discounted_amount"] = discounted_amount
            request.session["cart"]["cart_discount"]["amount_payable"] = amount_payable
            request.session.modified = True
        discount = request.session["cart"]["cart_discount"]
        
    checkout_url = reverse("store:checkout")
    count = len(request.session["cart"]["cart_items"].keys())
    delivery_address = None if not request.session["cart"].get("delivery_address", False) else request.session["cart"]["delivery_address"]
    return JsonResponse({
        "success": True,
        "cart": items,
        "total": total,
        "currency": currency,
        "discount": discount,
        "checkout_url": checkout_url,
        "items_count": count,
        "delivery_address": delivery_address 
    })
    

def removeFromCart(request):
    if request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    vid = request.POST["vid"]
    if not vid:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        vid = int(vid)
        v = Variation.objects.get(id=vid)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    varid = str(vid)
    if not request.session.get("cart", False) or not request.session["cart"].get("cart_items", False) \
        or varid not in request.session["cart"]["cart_items"]:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    qty = request.session["cart"]["cart_items"].pop(varid)

    if not request.session["cart"].get("cart_amount", False):
        request.session["cart"]["cart_amount"] = get_cart_amount(request)
    else:
        price = float(v.price)
        amount = math.ceil(qty*price)
        request.session["cart"]["cart_amount"] -= amount
    
    request.session.modified = True
    count = len(request.session["cart"]["cart_items"].keys())
    amount = request.session["cart"]["cart_amount"]

    if not count or not amount:
        request.session["cart"].clear()
        request.session.pop("cart", False)
        return JsonResponse({"success": True, "cart": False})
    
    if request.session["cart"].get("cart_discount", False):
        dp = request.session["cart"]["cart_discount"]["percent"]
        discounted_amount = math.floor((float(amount*dp))/100)
        amount_payable = amount - discounted_amount
        request.session["cart"]["cart_discount"]["discounted_amount"] = discounted_amount
        request.session["cart"]["cart_discount"]["amount_payable"] = amount_payable
        request.session.modified = True
        discount = request.session["cart"]["cart_discount"]
    else:
        discount = False

    return JsonResponse({"success": True, "count": count, "amount": amount, "cart": True, "discount": discount})


def get_cart_amount(request):
    if not request.session.get("cart", False) or not request.session["cart"].get("cart_items", False):
        return 0
    
    total = 0
    for vid, qty in request.session["cart"]["cart_items"].items():
        try:
            varid = int(vid)
            v = Variation.objects.get(id=varid)
        except:
            pass
        else:
            price = float(v.price)
            amount = math.ceil(qty*price)
            total += amount
    
    return total


def apply_discount(request):
    if request.method == "GET" or not request.session.get("cart", False) or not request.session["cart"].get("cart_items", False):
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    code = request.POST["code"]
    if not code:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        discount = Discount.objects.get(code=code)
    except:
        return JsonResponse({"success": False, "message": "Invalid Code"})
    
    if not request.session["cart"].get("cart_amount", False):
        request.session["cart"]["cart_amount"] = get_cart_amount(request)
        request.session.modified = True
    
    amount = request.session["cart"]["cart_amount"]
    dp = discount.percent
    discounted_amount = math.floor((float(amount*dp))/100)
    amount_payable = amount - discounted_amount
    
    try:
        currency = settings.CURRENCY
    except AttributeError:
        currency = "Rs."

    request.session["cart"]["cart_discount"] = {
        "code": code,
        "percent": discount.percent,
        "discounted_amount": discounted_amount,
        "amount_payable": amount_payable,
        "currency": currency
    }
    request.session.modified = True
    return JsonResponse({"success": True, "discount": request.session["cart"]["cart_discount"]})
    

def clearCart(request):
    if request.session.get("cart", False):
        request.session["cart"].clear()
        request.session.pop("cart", False)
    return JsonResponse({"success": True})


@login_required
@ensure_csrf_cookie
def checkout(request):
    if not request.session.get("cart", False):
        return HttpResponseRedirect(reverse("store:homepage"))
    
    return render(
        request,
        "store/checkout.html"
    )


@login_required
def getUserAddress(request):
    addresses = request.user.person.address.all()
    if not addresses or len(addresses) == 0:
        return JsonResponse({"success": False})
    
    a = []
    for address in addresses:
        a.append({
            "id": address.id,
            "first_name": address.first_name,
            "last_name": address.last_name,
            "email": address.email,
            "mobile": address.mobile,
            "homephone": address.homephone,
            "address1": address.address1,
            "address2": address.address2,
            "landmark": address.landmark,
            "pincode": address.pincode,
            "city": address.city,
            "state": address.state,
            "country": address.country
        })
    
    return JsonResponse({"success": True, "address": a})


@login_required
def addDeliveryAddress2Cart(request):
    if request.method == "GET" or not request.session.get("cart", False) or not request.session["cart"].get("cart_items", False):
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    address_id = request.POST["address_id"]
    if not address_id:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        address_id = int(address_id)
        address = Address.objects.get(id=address_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if address.person.user != request.user:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    request.session["cart"]["delivery_address"] = {
        "id": address.id,
        "first_name": address.first_name,
        "last_name": address.last_name,
        "email": address.email,
        "mobile": address.mobile,
        "homephone": address.homephone,
        "address1": address.address1,
        "address2": address.address2,
        "landmark": address.landmark,
        "pincode": address.pincode,
        "city": address.city,
        "state": address.state,
        "country": address.country
    }
    request.session.modified = True
    return JsonResponse({"success": True, "delivery_address": request.session["cart"]["delivery_address"]})


@login_required
def removeSelectedDeliveryAddress2Cart(request):
    if request.method == "GET" or not request.session.get("cart", False) \
        or not request.session["cart"].get("cart_items", False) \
            or not request.session["cart"].get("delivery_address", False):
            return JsonResponse({"success": False, "message": "Invalid Request"})
    
    address_id = request.POST["address_id"]
    if not address_id:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        address_id = int(address_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if request.session["cart"]["delivery_address"]["id"] != address_id:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    request.session["cart"]["delivery_address"].clear()
    request.session["cart"].pop("delivery_address", False)
    request.session.modified = True
    return JsonResponse({"success": True})


@login_required
def addNewDeliveryAddress2Cart(request):
    if request.method == "GET" or not request.session.get("cart", False) or not request.session["cart"].get("cart_items", False):
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    first_name = request.POST["first_name"]
    last_name = request.POST["last_name"]
    mobile = request.POST["mobile"]
    homephone = request.POST["homephone"]
    address1 = request.POST["address1"]
    address2 = request.POST["address2"]
    city = request.POST["city"]
    pincode = request.POST["pincode"]
    state = request.POST["state"]
    country = request.POST["country"]
    landmark = request.POST["landmark"]
    email = request.POST["email"]

    if not first_name or not last_name or not mobile or not address1 or not city \
        or not pincode or not state or not country or not landmark or not email:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    if not validate_email(email):
        return JsonResponse({"success": False, "message": "Invalid Email"})
    
    address = Address.objects.create(
        person=request.user.person,
        first_name=first_name.strip().lower().title(),
        last_name=last_name.strip().lower().title(),
        email=email,
        mobile=mobile,
        homephone=None if not homephone else homephone,
        address1=address1.strip().lower().title(),
        address2=None if not address2 else address2.strip().lower().title(),
        landmark=landmark.strip().lower().title(),
        pincode=pincode.strip(),
        city=city.strip().lower().title(),
        state=state.strip().lower().title(),
        country=country.strip().lower().title()
    )

    request.session["cart"]["delivery_address"] = {
        "id": address.id,
        "first_name": address.first_name,
        "last_name": address.last_name,
        "email": address.email,
        "mobile": address.mobile,
        "homephone": address.homephone,
        "address1": address.address1,
        "address2": address.address2,
        "landmark": address.landmark,
        "pincode": address.pincode,
        "city": address.city,
        "state": address.state,
        "country": address.country
    }
    request.session.modified = True
    return JsonResponse({"success": True, "delivery_address": request.session["cart"]["delivery_address"]})


@login_required
def place_order(request):
    if not request.session.get("cart", False) or not request.session["cart"].get("cart_items", False) \
        or not request.session["cart"].get("delivery_address", False) or request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    time = request.POST["time"]
    date = request.POST["date"]
    info = request.POST["info"]

    if info and len(info) > 200:
        return JsonResponse({"success": False, "message": "Maxinum 200 characters allowed."})

    if date and time:
        time_data = str(date) + ' ' + str(time)
        format_data = "%Y-%m-%d %H:%M"
        try:
            preferred_date = datetime.strptime(time_data, format_data)
        except:
            preferred_date = None
    elif date:
        time_data = str(date)
        format_data = "%Y-%m-%d"
        try:
            preferred_date = datetime.strptime(time_data, format_data)
        except:
            preferred_date = None
    else:
        preferred_date = None
    
    try:
        delivery_time_hours = settings.DELIVERY_TIME_IN_HOURS
    except AttributeError:
        delivery_time_hours = 24
    
    try:
        delivery_time_days = settings.DELIVERY_TIME_IN_DAYS
    except AttributeError:
        delivery_time_days = 1
    
    if preferred_date and (preferred_date - datetime.now()).days < delivery_time_days:
        return JsonResponse({"success": False, "message": f"We cannot deliver this product in less than {delivery_time_days} business day(s)."})

    address_id = request.session["cart"]["delivery_address"]["id"]
    try:
        address = Address.objects.get(id=address_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if address.person.user != request.user:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    discount = None
    amount_payable = request.session["cart"]["cart_amount"]
    discount_code = None if not request.session["cart"].get("cart_discount", False) else request.session["cart"]["cart_discount"]["code"]
    if discount_code:
        try:
            discount = Discount.objects.get(code=discount_code)
        except:
            pass
        else:
            amount_payable = request.session["cart"]["cart_discount"]["amount_payable"]
    
    try:
        with transaction.atomic():
            order = Order.objects.create(
                customer = request.user.person,
                address = address,
                amount = request.session["cart"]["cart_amount"],
                discount = discount,
                amount_payable = amount_payable,
                preferred_delivery_time = preferred_date,
                additional_info = None if not info else info,
                count = len(request.session["cart"]["cart_items"].keys())
            )

            for vid, qty in request.session["cart"]["cart_items"].items():
                vid = int(vid)
                v = Variation.objects.get(id=vid)
                order_item = OrderItem.objects.create(
                    order = order,
                    product = v,
                    quantity = qty,
                    unit_price = v.price,
                    amount = math.ceil(float(v.price)*qty)
                )
    except:
        request.session["cart"].clear()
        request.session.pop("cart", False)
        return_url = reverse('store:homepage')
        messages.add_message(
            request,
            messages.ERROR,
            "Something went wrong. Please try again later."
        )
        return JsonResponse({"success": True, "return_url": return_url})
    
    request.session["cart"].clear()
    request.session.pop("cart", False)
    
    messages.add_message(
        request,
        messages.SUCCESS,
        "Thank you for your order."
    )
    return_url = reverse("store:order", kwargs={'order_id': order.id})
    return JsonResponse({"success": True, "return_url": return_url})


@login_required
@ensure_csrf_cookie
def orders(request):
    orders = get_orders(request)
    return render(
        request,
        "store/orders.html",
        {"orders": orders}
    )


@login_required
@ensure_csrf_cookie
def order(request, order_id):
    order_details = get_order_details(request, order_id)
    if not order_details:
        return HttpResponseRedirect(reverse("store:orders"))
    return render(
        request,
        'store/order.html',
        {"order": order_details}
    )


@login_required
def cancelOrder(request):
    if request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    order_id = request.POST["order_id"]
    reason = request.POST["reason"]

    if not order_id:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    if reason and len(reason) > 200:
        return JsonResponse({"success": False, "message": "Maxinum 200 characters allowed."})
    
    try:
        order_id = int(order_id)
        order = Order.objects.get(id=order_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if order.customer != request.user.person or order.status != 'O':
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        with transaction.atomic():
            oc = OrderCancellation.objects.create(
                order = order,
                reason = None if not reason else reason
            )
            order.status = 'P'
            order.save()
    except:
        return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    return JsonResponse({"success": True})


@login_required
def reopenOrder(request, order_id):
    try:
        order_id = int(order_id)
        order = Order.objects.get(id=order_id)
    except:
        return HttpResponseRedirect(reverse("store:orders"))
    
    if order.customer != request.user.person:
        return HttpResponseRedirect(reverse("store:orders"))
    
    if order.status != 'P':
        messages.add_message(
            request,
            messages.INFO,
            "You cannot reopen this order. Kindly place a fresh order."
        )
        return HttpResponseRedirect(reverse("store:order", kwargs={'order_id': order_id}))
    
    try:
        delivery_time_days = settings.DELIVERY_TIME_IN_DAYS
    except AttributeError:
        delivery_time_days = 1
    
    try:
        with transaction.atomic():
            if order.preferred_delivery_time and (order.preferred_delivery_time - datetime.now(timezone.utc)).days < delivery_time_days:
                order.preferred_delivery_time = None
            
            order.status = 'O'
            order.placed_at = datetime.now()
            order.save()
            order.cancellation.delete()
    except:
        messages.add_message(
            request,
            messages.ERROR,
            "Something went wrong. Please try again later."
        )
        return HttpResponseRedirect(reverse("store:order", kwargs={'order_id': order_id}))
    
    messages.add_message(
        request,
        messages.SUCCESS,
        "Your order is active."
    )
    return HttpResponseRedirect(reverse("store:order", kwargs={'order_id': order_id}))


def search(request):
    q = request.GET.get('q')
    if not q:
        return HttpResponseRedirect(reverse("store:homepage"))
    
    products = get_search_products(request, q)
    return render(
        request,
        "store/search.html",
        {"products": products, "search": True, "q": q}
    )


@login_required
def database_update(request):
    if request.user.is_superuser:
        database.UPLOAD_CATEGORIES()
        database.UPLOAD_PRODUCTS()
        database.UPLOAD_TAGS()
        database.UPDATE_PROUCTS()
        database.UPDATE_KEYVALUE()
        database.UPDATE_VARIATIONS()
        database.inventory()
    return HttpResponseRedirect(reverse("store:homepage"))


@login_required
def clear_database_but_images(request):
    if request.user.is_superuser:
        database.clear_all_but_images()
    return HttpResponseRedirect(reverse("store:homepage"))


@login_required
def clear_database_images(request):
    if request.user.is_superuser:
        database.clear_images()
    return HttpResponseRedirect(reverse("store:homepage"))