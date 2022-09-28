from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils.timezone import make_aware
from time import sleep
from datetime import datetime, timedelta
from .models import Discount, Order, Product, Address, Pincode, Variation, OrderItem, OrderCancellation
from . import utility
from django.views.decorators.csrf import ensure_csrf_cookie


### Store Homepage
@ensure_csrf_cookie
def homepage(request):
    context = utility.get_products(request)
    return render(
        request,
        "store/homepage.html",
        context
    )


### get category wise products for homepage product filter
def getProducts(request):
    if request.method == "GET":
        return HttpResponseRedirect(reverse('store:homepage'))
    category = request.POST["category"]
    p = []
    if not category:
        return JsonResponse({"products": p})
    
    products = Product.objects.filter(categories__slug=category)
    for product in products:
        p.append({
            "slug": product.slug,
            "title": product.title
        })
    return JsonResponse({"products": p})


### add product to cart
def add2cart(request):
    if request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    qty = request.POST["qty"]
    variation_id = request.POST["variation_id"]

    if not qty or not variation_id:
        return JsonResponse({"success": False})
    
    response = utility.add_item_to_cart(request, variation_id, qty)
    return JsonResponse(response)


### display cart offcanvas
def getCart(request):
    if not request.session.get("cart", False):
        return JsonResponse({"success": False})
    count = len(request.session["cart"]["cart_items"].keys())
    return JsonResponse({"success": True, "count": count, "cart": request.session["cart"]})


def clear_cart_items(request):
    if request.session.get("cart", False):
        request.session["cart"].clear()
        request.session.pop("cart", False)
        request.session.modified = True
    return


### clear cart
def clearCart(request):
    clear_cart_items(request)
    return JsonResponse({"success": True})


### remove product from cart
def removeFromCart(request):
    if request.method == "GET" or not request.session.get("cart", False):
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    variation_id = request.POST["variation_id"]
    if not variation_id:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    response = utility.remove_item_from_cart(request, variation_id)
    return JsonResponse(response)


### apply cart level discount
def apply_discount(request):
    if request.method == "GET" or not request.session.get("cart", False):
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    code = request.POST["code"]
    if not code:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        discount = Discount.objects.get(code=code)
    except:
        return JsonResponse({"success": False, "message": "Incorrect Code"})
    
    if request.session["cart"]["cart_amount"]["discount"]:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    request.session["cart"]["cart_amount"]["discount"] = discount.percent
    request.session["cart"]["cart_amount"]["discount_code"] = discount.code
    amount_payable = request.session["cart"]["cart_amount"]["amount_payable"]
    amount_payable = amount_payable - (amount_payable*(discount.percent/100))
    request.session["cart"]["cart_amount"]["amount_payable"] = round(amount_payable, 2)
    request.session.modified = True
    return JsonResponse({"success": True, "count": request.session["cart"]["count"], "cart": request.session["cart"]})


### checkout page
@ensure_csrf_cookie
@login_required
def checkout(request):
    if not request.session.get("cart", False):
        return HttpResponseRedirect(reverse('store:homepage'))

    return render(
        request,
        "store/checkout.html",
        {"cart": request.session["cart"]}
    )


### select a saved address
@login_required
def selectDeliveryAddress(request):
    if request.method == "GET" or not request.session.get("cart", False):
        return JsonResponse({"success": False})
    
    address_id = request.POST["address_id"]
    if not address_id:
        return JsonResponse({"success": False})
    
    try:
        address_id = int(address_id)
        a = Address.objects.select_related("user").get(id=address_id)
    except:
        return JsonResponse({"success": False})
    
    if a.user != request.user:
        return JsonResponse({"success": False})
    
    address = {
        "id": a.id,
        "editable": a.editable,
        "is_primary": a.is_primary,
        "first_name": a.first_name,
        "last_name": a.last_name,
        "email": a.email,
        "mobile": a.mobile,
        "landline": None if not a.landline else a.landline,
        "address1": a.address1,
        "address2": None if not a.address2 else a.address2,
        "landmark": a.landmark,
        "pincode": a.pincode,
        "city": a.city,
        "state": a.state,
        "country": a.country
    }

    request.session["cart"].pop("delivery_address", None)
    request.session["cart"]["delivery_address"] = address

    if settings.CHECK_DELIVERABILITY:
        items = list(request.session["cart"]["cart_items"].values())
        for item in items:
            vid = str(item["id"])
            request.session["cart"]["cart_items"][vid]["zipcode_availability"] = utility.check_availability(
                a.pincode,
                item["id"],
                request.session["cart"]["cart_items"][vid]["delivery_time_in_days"]
            )
    request.session.modified = True
    return JsonResponse({"success": True, "address": address, "cart": request.session["cart"]})


### get delivery addresses
@login_required
def getDeliveryAddress(request):
    if not request.session.get("cart", False):
        return JsonResponse({"success": False})

    address = request.user.address.all()
    if not address:
        return JsonResponse({"success": True, "address": None})
    add = []
    for a in address:
        if request.session["cart"].get("delivery_address", False) and a.id == request.session["cart"]["delivery_address"]["id"]:
            selected = True
        else:
            selected = False
        add.append({
            "id": a.id,
            "editable": a.editable,
            "is_primary": a.is_primary,
            "first_name": a.first_name,
            "last_name": a.last_name,
            "email": a.email,
            "mobile": a.mobile,
            "landline": None if not a.landline else a.landline,
            "address1": a.address1,
            "address2": None if not a.address2 else a.address2,
            "landmark": a.landmark,
            "pincode": a.pincode,
            "city": a.city,
            "state": a.state,
            "country": a.country,
            "selected_address": selected
        })
    return JsonResponse({"success": True, "address": add})


### remove Selected Delivery Address
@login_required
def removeSelectedDeliveryAddress(request):
    if request.method == "GET" or not request.session.get("cart", False) or not request.session["cart"].get("delivery_address", False):
        return JsonResponse({"success": False})
    
    address_id = request.POST["address_id"]
    if not address_id:
        return JsonResponse({"success": False})
    
    try:
        address_id = int(address_id)
        a = Address.objects.select_related("user").get(id=address_id)
    except:
        return JsonResponse({"success": False})
    
    if a.user != request.user or address_id != request.session["cart"]["delivery_address"]["id"]:
        return JsonResponse({"success": False})
    
    request.session["cart"]["delivery_address"].clear()
    request.session["cart"].pop("delivery_address", None)

    if settings.CHECK_DELIVERABILITY:
        items = list(request.session["cart"]["cart_items"].values())
        for item in items:
            vid = str(item["id"])
            request.session["cart"]["cart_items"][vid]["zipcode_availability"] = None
    request.session.modified = True
    return JsonResponse({"success": True, "cart": request.session["cart"]})


### place order
@login_required
def placeOrder(request):
    if request.method == "GET" or not request.session.get("cart", False) or not request.session["cart"].get("delivery_address", False):
        return JsonResponse({
            "success": False,
            "reload": True,
            "reload_url": reverse("store:homepage")
        })
    
    pdt = request.POST["datetime"]
    payment_method = request.POST["payment_method"]
    if not payment_method:
        return JsonResponse({"success": False, "message": "Please select a payment method."})
    
    if payment_method not in ["CCD", "DCD", "PPL", "OTH", "COD"]:
        clear_cart_items(request)
        return JsonResponse({
            "success": False,
            "reload": True,
            "reload_url": reverse("store:homepage")
        })
    
    dt = None if not pdt else utility.get_preferred_delivery_time(pdt)
    if settings.CHECK_DELIVERABILITY:
        d = utility.deliveverable_at_location(request, request.session["cart"]["delivery_address"]["pincode"])
        if not d["deliverability"]:
            return JsonResponse({
                "success": False,
                "message": "Home delivery is not available at your location."
            })
        elif not d["availability"]:
            return JsonResponse({
                "success": False,
                "message": f'Please remove the items that are not deliverable at your location, {request.session["cart"]["delivery_address"]["pincode"]}, and try again.'
            })
    
    max_time = utility.max_delivery_time(request, request.session["cart"]["delivery_address"]["pincode"])
    if dt and (dt - datetime.now()).days < max_time:
        return JsonResponse({"success": False, "message": f"We cannot deliver your order in less than {max_time} business day(s)."})
    elif not dt:
        dt = datetime.now() + timedelta(days=max_time)
    
    discount_code = None if not request.session["cart"]["cart_amount"]["discount_code"] else request.session["cart"]["cart_amount"]["discount_code"]
    if discount_code:
        try:
            discount = Discount.objects.get(code=discount_code)
        except:
            clear_cart_items(request)
            return JsonResponse({
                "success": False,
                "reload": True,
                "reload_url": reverse("store:homepage")
            })
        else:
            if Order.objects.filter(customer=request.user, discount=discount).exists():
                request.session["cart"]["cart_amount"]["amount_payable"] = request.session["cart"]["cart_amount"]["amount"]
                request.session["cart"]["cart_amount"]["discount_code"] = None
                request.session["cart"]["cart_amount"]["discount"] = 0
                request.session.modified = True
                messages.add_message(request, messages.ERROR, "You cannot use a discount code twice.")
                return JsonResponse({
                    "success": False,
                    "reload": True,
                    "reload_url": reverse("store:checkout")
                })
    else:
        discount = None
    
    address_id = request.session["cart"]["delivery_address"]["id"]
    try:
        address = Address.objects.select_related("user").get(id=address_id)
    except:
        clear_cart_items(request)
        return JsonResponse({
            "success": False,
            "reload": True,
            "reload_url": reverse("store:homepage")
        })
    if address.user != request.user:
        clear_cart_items(request)
        return JsonResponse({
            "success": False,
            "reload": True,
            "reload_url": reverse("store:homepage")
        })
    
    response = utility.check_inventory(list(request.session["cart"]["cart_items"].values()))
    if not response["success"]:
        return JsonResponse(response)
    
    try:
        with transaction.atomic():
            order = Order.objects.create(
                customer = request.user,
                address = address,
                amount = request.session["cart"]["cart_amount"]["amount"],
                discount = discount,
                amount_payable = request.session["cart"]["cart_amount"]["amount_payable"],
                payment_method = payment_method,
                expected_delivery_time = make_aware(dt),
                count = request.session["cart"]["count"]
            )

            for item in request.session["cart"]["cart_items"].values():
                v = Variation.objects.get(id=item["id"])
                order_item = OrderItem.objects.create(
                    order = order,
                    product = v,
                    unit_price = item["unit_price"],
                    quantity = item["qty"],
                    amount = item["amount"],
                    discount_percent = item["discount"],
                    amount_payable = item["amount_payable"]
                )
                v.inventory -= item["qty"]
                if v.inventory <= 0:
                    v.availability = False
                v.save()
            address.editable = False
            address.save()
    except:
        messages.add_message(
            request,
            messages.ERROR,
            "Something went wrong. Please try again later."
        )
        return JsonResponse({
            "success": False,
            "reload": True,
            "reload_url": reverse("store:checkout")
        })
    
    clear_cart_items(request)
    messages.add_message(
        request,
        messages.SUCCESS,
        "Thank you for your order."
    )
    return_url = reverse("store:order", kwargs={'order_id': order.id})
    return JsonResponse({"success": True, "return_url": return_url})


### all orders page
@ensure_csrf_cookie
@login_required
def orders(request):
    orders = utility.get_all_orders(request)
    return render(
        request,
        "store/orders.html",
        {"orders": orders}
    )


### single order page
@ensure_csrf_cookie
@login_required
def order(request, order_id):
    try:
        order_id = int(order_id)
    except ValueError:
        return HttpResponseRedirect(reverse("store:orders"))
    
    order = Order.objects.select_related(
        "address",
        "discount",
        "cancellation",
    ).prefetch_related(
        "orderitems__product__product",
        "orderitems__product__keyvalues__key",
        "orderitems__product__keyvalues__value",
    ).filter(
        id=order_id,
        customer=request.user
    ).first()

    if not order:
        return HttpResponseRedirect(reverse("store:orders"))
    
    return render(
        request,
        "store/order.html",
        {"order": order}
    )


@login_required
def cancelOrder(request):
    if request.method == "GET":
        return JsonResponse({"success": False})
    
    order_id = request.POST["order_id"]
    if not order_id:
        return JsonResponse({"success": False})
    
    try:
        order_id = int(order_id)
    except ValueError:
        return JsonResponse({"success": False})
    
    order = Order.objects.filter(id=order_id, customer=request.user, order_status='O').first()
    if not order:
        return JsonResponse({"success": False})
    
    try:
        with transaction.atomic():
            order.order_status = 'P'
            order.payment_status = 'U'
            order.save()
            
            oc = OrderCancellation.objects.create(
                order = order
            )
    except:
        messages.add_message(
            request,
            messages.ERROR,
            "Something went wrong. Please try again later."
        )
        return JsonResponse({
            "success": True,
            "redirect_url": reverse("store:order", kwargs={'order_id': order_id})
        })
    else:
        messages.add_message(
            request,
            messages.SUCCESS,
            "Your request for cancellation is being processed."
        )
        return JsonResponse({
            "success": True,
            "redirect_url": reverse("store:order", kwargs={'order_id': order_id})
        })


### Search page
@ensure_csrf_cookie
def search(request):
    response = utility.get_search_products(request)
    if not response:
        return HttpResponseRedirect(reverse("store:homepage"))

    return render(
        request,
        "store/search.html",
        {
            "products": response["products"],
            "search_query": response["search_query"],
            "search_filter_query": response["search_filter_query"]
        }
    )


### Products page not configured
@ensure_csrf_cookie
def products(request, product_slug):
    return render(
        request,
        "store/products.html"
    )


### product variations page
@ensure_csrf_cookie
def product(request, product_slug, variation_id):
    try:
        variation_id = int(variation_id)
    except ValueError:
        return HttpResponseRedirect(reverse("store:homepage"))

    variation = Variation.objects.select_related(
        "product",
        "discount"
    ).prefetch_related(
        "product__categories",
        "keyvalues",
        "images",
        "keyvalues__key",
        "keyvalues__value"
    ).filter(
        id = variation_id,
        product__slug = product_slug
    ).first()

    if not variation:
        return HttpResponseRedirect(reverse("store:homepage"))
    return render(
        request,
        "store/product.html",
        {
            "product": variation,
            "product_slug": product_slug,
            "checkDeliverability": settings.CHECK_DELIVERABILITY
        }
    )


def checkDeliverability(request):
    if request.method == "GET":
        return HttpResponseRedirect(reverse("store:homepage"))
    
    pincode  =request.POST["pincode"]
    variation_id = request.POST["variation_id"]

    if not pincode or not variation_id:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    try:
        variation_id = int(variation_id)
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    pincode = Pincode.objects.filter(pincode=pincode).first()
    if not pincode:
        return JsonResponse({"success": False, "message": "Sorry! Home delivery is not available at this location."})
    
    if Pincode.objects.filter(products_unavailable__id=variation_id).exists():
        return JsonResponse({"success": False, "message": "Sorry! This product is not deliverable at this location."})
    

    v = Variation.objects.filter(id=variation_id).first()
    if not v:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    m = max([v.delivery_time_in_days, pincode.delivery_time_in_days])
    return JsonResponse({"success": True, "message": f"Available! Delivery Time: {m} business day(s)."})
    

    
    





    



    







    
    
    

    




        

### user profile
@ensure_csrf_cookie
@login_required
def profile(request):
    return render(
        request,
        "store/profile.html"
    )


### get user info
@login_required
def getUser(request):
    user = {
        "authentication_account": reverse("authentication:account"),
        "date_joined": request.user.date_joined,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "username": request.user.username,
        "email": request.user.email,
        "last_login": request.user.last_login
    }
    address = request.user.address.all()
    if not address:
        return JsonResponse({"success": True, "address": None, "user": user})
    add = []
    for a in address:
        add.append({
            "id": a.id,
            "editable": a.editable,
            "is_primary": a.is_primary,
            "first_name": a.first_name,
            "last_name": a.last_name,
            "email": a.email,
            "mobile": a.mobile,
            "landline": None if not a.landline else a.landline,
            "address1": a.address1,
            "address2": None if not a.address2 else a.address2,
            "landmark": a.landmark,
            "pincode": a.pincode,
            "city": a.city,
            "state": a.state,
            "country": a.country
        })
    return JsonResponse({"success": True, "address": add, "user": user})


### add a delivery address
@login_required
def addAddress(request):
    if request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    first_name = request.POST["first_name"]
    last_name = request.POST["last_name"]
    email = request.POST["email"]
    mobile = request.POST["mobile"]
    landline = request.POST["landline"]
    landmark = request.POST["landmark"]
    address1 = request.POST["address1"]
    address2 = request.POST["address2"]
    city = request.POST["city"]
    pincode = request.POST["pincode"]
    state = request.POST["state"]
    country = request.POST["country"]
    if not first_name or not last_name or not email or not mobile or not landmark or not address1 \
        or not city or not pincode or not state or not country:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    if not utility.validate_email(email):
        return JsonResponse({"success": False, "message": "Invalid Email"})
    
    try:
        a = Address.objects.create(
            user = request.user,
            first_name = first_name.strip().lower().title(),
            last_name = last_name.strip().lower().title(),
            email = email,
            mobile = mobile,
            landline = None if not landline else landline,
            address1 = address1.strip().lower().title(),
            address2 = None if not address2 else address2.strip().lower().title(),
            landmark = landmark.strip().lower().title(),
            pincode = pincode,
            city = city.strip().lower().title(),
            state = state.strip().lower().title(),
            country = country.strip().lower().title()
        )
    except:
        return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    address = {
        "id": a.id,
        "editable": a.editable,
        "is_primary": a.is_primary,
        "first_name": a.first_name,
        "last_name": a.last_name,
        "email": a.email,
        "mobile": a.mobile,
        "landline": None if not a.landline else a.landline,
        "address1": a.address1,
        "address2": None if not a.address2 else a.address2,
        "landmark": a.landmark,
        "pincode": a.pincode,
        "city": a.city,
        "state": a.state,
        "country": a.country
    }
    return JsonResponse({"success": True, "address": address})


### set primary address
@login_required
def makeAddressPrimary(request):
    if request.method == "GET":
        return JsonResponse({"success": False})
    
    address_id = request.POST["address_id"]
    if not address_id:
        return JsonResponse({"success": False})
    
    try:
        address_id = int(address_id)
        address = Address.objects.get(id=address_id)
    except:
        return JsonResponse({"success": False})
    
    if address.user != request.user:
        return JsonResponse({"success": False})
    
    addresses = request.user.address.all()
    for a in addresses:
        if a == address:
            a.is_primary = True
        else:
            a.is_primary = False
        a.save()
    
    return JsonResponse({"success": True})


### delete delivery address
@login_required
def deleteAddress(request):
    if request.method == "GET":
        return JsonResponse({"success": False})
    
    address_id = request.POST["address_id"]
    if not address_id:
        return JsonResponse({"success": False})
    
    try:
        address_id = int(address_id)
        address = Address.objects.get(id=address_id)
    except:
        return JsonResponse({"success": False})
    
    if address.user != request.user or not address.editable or address.orders.exists():
        return JsonResponse({"success": False})
        
    try:
        address.delete()
    except:
        return JsonResponse({"success": False})
    else:
        return JsonResponse({"success": True})


### get user delivery address
@login_required
def getAddress(request):
    if request.method == "GET":
        return JsonResponse({"success": False})
    
    address_id = request.POST["address_id"]
    if not address_id:
        return JsonResponse({"success": False})
    
    try:
        address_id = int(address_id)
        a = Address.objects.get(id=address_id)
    except:
        return JsonResponse({"success": False})
    
    if a.user != request.user or not a.editable or a.orders.exists():
        return JsonResponse({"success": False})
    
    address = {
        "id": a.id,
        "first_name": a.first_name,
        "last_name": a.last_name,
        "email": a.email,
        "mobile": a.mobile,
        "landline": None if not a.landline else a.landline,
        "address1": a.address1,
        "address2": None if not a.address2 else a.address2,
        "landmark": a.landmark,
        "pincode": a.pincode,
        "city": a.city,
        "state": a.state,
        "country": a.country
    }
            
    return JsonResponse({"success": True, "address": address})


### edit delivery address
@login_required
def editAddress(request):
    if request.method == "GET":
        return JsonResponse({"success": False, "message":"Invalid Request"})
    
    address_id = request.POST["address_id"]
    if not address_id:
        return JsonResponse({"success": False, "message":"Invalid Request"})
    
    try:
        address_id = int(address_id)
        a = Address.objects.get(id=address_id)
    except:
        return JsonResponse({"success": False, "message":"Invalid Request"})
    
    if a.user != request.user or not a.editable or a.orders.exists():
        return JsonResponse({"success": False, "message":"Invalid Request"})
    
    first_name = request.POST["first_name"]
    last_name = request.POST["last_name"]
    email = request.POST["email"]
    mobile = request.POST["mobile"]
    landline = request.POST["landline"]
    landmark = request.POST["landmark"]
    address1 = request.POST["address1"]
    address2 = request.POST["address2"]
    city = request.POST["city"]
    pincode = request.POST["pincode"]
    state = request.POST["state"]
    country = request.POST["country"]
    if not first_name or not last_name or not email or not mobile or not landmark or not address1 \
        or not city or not pincode or not state or not country:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    if not utility.validate_email(email):
        return JsonResponse({"success": False, "message": "Invalid Email"})
    
    a.first_name = first_name.strip().lower().title()
    a.last_name = last_name.strip().lower().title()
    a.email = email
    a.mobile = mobile
    a.landline = None if not landline else landline
    a.address1 = address1.strip().lower().title()
    a.address2 = None if not address2 else address2.strip().lower().title()
    a.landmark = landmark.strip().lower().title()
    a.pincode = pincode
    a.city = city.strip().lower().title()
    a.state = state.strip().lower().title()
    a.country = country.strip().lower().title()
    try:
        a.save()
    except:
        return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    return JsonResponse({"success": True})