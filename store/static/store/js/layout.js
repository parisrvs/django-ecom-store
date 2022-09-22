var prevent_default = false;
var cartPage = document.querySelector("#checkoutMainPage");
window.addEventListener('beforeunload', function (e) {
    if (prevent_default) {
        e.preventDefault();
        e.returnValue = 'Are you sure you want to cancel this process?';
    }
    return;
});

function disable() {
    document.querySelectorAll('.toDisable').forEach(b => {
        b.disabled = true;
    });
    document.querySelectorAll(".toHide").forEach(s => {
        s.hidden = false;
    });
    document.querySelectorAll(".toDisableAnchorTag").forEach(a => {
        a.style.pointerEvents="none";
        a.style.cursor="default";
    });
}


function enable() {
    document.querySelectorAll('.toDisable').forEach(b => {
        b.disabled = false;
    });
    document.querySelectorAll(".toHide").forEach(s => {
        s.hidden = true;
    });
    document.querySelectorAll(".toDisableAnchorTag").forEach(a => {
        a.style.pointerEvents="auto";
        a.style.cursor="pointer";
    });
}



function search(event) {
    let q = document.querySelector("#navBarSearchInput").value.replace(/^\s+|\s+$/g, '');
    if (!q) {
        event.preventDefault();
        document.querySelector("#navbarSearchBtn").blur();
        return false;
    }
}


function displayCart(event) {
    event.preventDefault();
    const request = new XMLHttpRequest();
    request.open('GET', '/store/get-cart/');

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            const details_template = Handlebars.compile(document.querySelector('#cartOffcanvasHandlebars').innerHTML);
            const details = details_template({"cart": res.cart, "count": res.count});
            document.querySelector("#cartOffcanvasDiv").innerHTML = details;
            document.querySelector("#cartOffcanvasDisplayBtn").click();
        }
    };

    request.send();
    return false;
}


function removeFromCart(event, variation_id) {
    event.preventDefault();

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/remove-from-cart/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            if (res.cart) {
                const details_template = Handlebars.compile(document.querySelector('#cartOffcanvasHandlebars').innerHTML);
                const details = details_template({"cart": res.cart, "count": res.count});
                document.querySelector("#cartOffcanvasDiv").innerHTML = details;
                if (cartPage) {
                    const cart_template = Handlebars.compile(document.querySelector('#checkoutPageCartItemsHandlebars').innerHTML);
                    const cart = cart_template({"cart": res.cart});
                    document.querySelector("#cart_items").innerHTML = cart;
                }
            } else {
                document.querySelector("#cartOffcanvasCloseBtn").click();
                if (cartPage)
                    location.reload();
            }
            update_cart_count(res.count);
        }
    };

    const data = new FormData();
    data.append('variation_id', variation_id);
    request.send(data);
    return false;
}


function update_cart_count(count) {
    document.querySelectorAll(".cart_items_count").forEach(i => {
        i.innerHTML = count;
    });
    return;
}


function applyDiscount(event) {
    event.preventDefault();

    let code = document.querySelector("#cartDiscountFormInput").value.replace(/^\s+|\s+$/g, '');
    if (!code) {
        document.querySelector("#cartDiscountFormSubmitBtn").blur();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/apply-discount/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            const details_template = Handlebars.compile(document.querySelector('#cartOffcanvasHandlebars').innerHTML);
            const details = details_template({"cart": res.cart, "count": res.count});
            document.querySelector("#cartOffcanvasDiv").innerHTML = details;
            if (cartPage) {
                const cart_template = Handlebars.compile(document.querySelector('#checkoutPageCartItemsHandlebars').innerHTML);
                const cart = cart_template({"cart": res.cart});
                document.querySelector("#cart_items").innerHTML = cart;
            }
        } else {
            document.querySelector("#cartDiscountFormSubmitBtn").blur();
            document.querySelector("#discountCodeError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('code', code);
    request.send(data);
    return false;
}


function clearCart(event) {
    event.preventDefault();
    const request = new XMLHttpRequest();
    request.open('GET', '/store/clear-cart/');

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            document.querySelector("#cartOffcanvasCloseBtn").click();
            update_cart_count(0);
            if (cartPage)
                location.reload();
        }
    };

    request.send();
    return false;
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}