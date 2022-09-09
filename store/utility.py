from .models import Order

def get_order_details(request, order_id):
    try:
        order_id = int(order_id)
        order = Order.objects.select_related("address", "discount", "cancellation").get(id=order_id)
    except:
        return None
    if order.customer != request.user.person:
        return None
    
    items = order.orderitems.select_related().all()
    i = []
    for item in items:
        k_v = []
        keyvalues = item.product.keyvalues.select_related("key", "value").all()
        for kv in keyvalues:
            k_v.append({
                "key": kv.key.key.strip().lower().title(),
                "value": kv.value.value.strip().lower().title(),
            })

        i.append({
            "id": item.id,
            "product": {
                "product_title": item.product.product.title.strip().lower().title(),
                "product_slug": item.product.product.slug,
                "variation_id": item.product.id,
                "unit": item.product.unit.strip().lower().title(),
                "price": round(float(item.product.price), 2),
                "keyvalues": k_v
            },
            "qty": item.quantity,
            "unit_price": item.unit_price,
            "amount": round(float(item.amount), 2)
        })
    
    if order.status == 'P':
        cancellation = {
            "cancelled_at": order.cancellation.cancelled_at,
            "reason": order.cancellation.reason
        }
    else:
        cancellation = None

    o = {
        "id": order.id,
        "address": {
            "id": order.address.id,
            "first_name": order.address.first_name,
            "last_name": order.address.last_name,
            "email": order.address.email,
            "mobile": order.address.mobile,
            "homephone": order.address.homephone,
            "address1": order.address.address1,
            "address2": order.address.address2,
            "landmark": order.address.landmark,
            "pincode": order.address.pincode,
            "city": order.address.city,
            "state": order.address.state,
            "country": order.address.country
        },
        "amount": order.amount,
        "discount": None if not order.discount else order.discount.percent,
        "amount_payable": order.amount_payable,
        "status": order.status,
        "placed_at": order.placed_at,
        "closed_at": order.closed_at,
        "cancelled_at": order.cancelled_at,
        "preferred_delivery_time": order.preferred_delivery_time,
        "additional_info": order.additional_info,
        "count": order.count,
        "items": i,
        "cancellation": cancellation
    }

    return o


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

