var prevent_default = false;
window.addEventListener('beforeunload', function (e) {
    if (prevent_default) {
        e.preventDefault();
        e.returnValue = 'Are you sure you want to cancel this process?';
    }
    return;
});


document.addEventListener("DOMContentLoaded", ()=>{
    document.querySelector("#navBarSearchForm").onsubmit = ()=>{
        let q = document.querySelector("#navBarSearchFormInput").value.replace(/^\s+|\s+$/g, '');
        if (!q) {
            document.querySelector("#navBarSearchBtn").blur();
            return false;
        }
    }
});


function do_nothing(event) {
    event.preventDefault();
    document.querySelector("#pagination_do_nothing").blur();
    return false;
}


function disable_buttons() {
    document.querySelectorAll('.toDisable').forEach(b => {
        b.disabled = true;
    });
    // document.querySelectorAll(".spinner-border").forEach(s => {
    //     s.hidden = false;
    // });
    document.querySelectorAll(".toDisableAnchorTag").forEach(a => {
        a.style.pointerEvents="none";
        a.style.cursor="default";
    });
}


function enable_buttons() {
    document.querySelectorAll('.toDisable').forEach(b => {
        b.disabled = false;
    });
    // document.querySelectorAll(".spinner-border").forEach(s => {
    //     s.hidden = true;
    // });
    document.querySelectorAll(".toDisableAnchorTag").forEach(a => {
        a.style.pointerEvents="auto";
        a.style.cursor="pointer";
    });
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

function displayCart(event) {
    event.preventDefault();

    const request = new XMLHttpRequest();
    request.open('GET', '/store/cart/');
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            const details_template = Handlebars.compile(document.querySelector('#cartOffcanvasHandlebars').innerHTML);
            const details = details_template({"cart": res.cart, "total": res.total, "currency": res.currency, "checkout_url": res.checkout_url});
            document.querySelector("#cartOffcanvasBody").innerHTML = details;

            if (res.discount) {
                const discountInfo_template = Handlebars.compile(document.querySelector('#cartOffcanvasDicountInfoHandlebars').innerHTML);
                const discount = discountInfo_template(res.discount);
                document.querySelector("#cartOffcanvasDiscount").innerHTML = discount;
            } else {
                const discountForm_template = Handlebars.compile(document.querySelector('#cartOffcanvasDicountFormHandlebars').innerHTML);
                const discount = discountForm_template();
                document.querySelector("#cartOffcanvasDiscount").innerHTML = discount;
            }
            document.querySelector("#cartOffcanvasDisplayBtn").click();
        } else {
            return false;
        }
    };
    request.send();
    return false;
}


function removeFromCart(event, vid) {
    event.preventDefault();

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/cart/remove-item/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            if (!res.cart) {
                document.querySelector("#cartOffcanvasCloseBtn").click();
                update_cart_count(0);
            } else {
                update_cart_count(res.count);
                document.querySelector("#cartTotalAmount").innerHTML = res.amount;
                let li_id = `cartItemList${vid}`;
                document.getElementById(li_id).remove();

                if (res.discount) {
                    const discountInfo_template = Handlebars.compile(document.querySelector('#cartOffcanvasDicountInfoHandlebars').innerHTML);
                    const discount = discountInfo_template(res.discount);
                    document.querySelector("#cartOffcanvasDiscount").innerHTML = discount;
                }
            }
            if (document.querySelector("#checkoutMainPage")) {
                load_cart();
                // setTimeout(load_cart, 1000);
            }
        } else {
            alert(res.message);
        }
    };

    const data = new FormData();
    data.append('vid', vid);
    request.send(data);
    return false;
}


function update_cart_count(count) {
    document.querySelectorAll(".totalCartItemsCount").forEach(l => {
        l.innerHTML = count;
    });
    return;
}


function applyDiscount(event) {
    event.preventDefault();
    let code = document.querySelector("#cartDiscountFormInput").value.replace(/^\s+|\s+$/g, '');
    if (!code) {
        document.querySelector("#cartDiscountFormSubmitBtn").blur();
        document.querySelector("#cartDiscountFormInput").focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/apply-discount/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    document.querySelector("#cartOffcanvasCloseBtn").disabled = true;
    disable_buttons();
    prevent_default = true;
    document.querySelector("#applyDiscountSpinner").hidden = false;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            document.querySelector("#cartOffcanvasCloseBtn").disabled = false;
            enable_buttons();
            prevent_default = false;
            document.querySelector("#applyDiscountSpinner").hidden = true;

            const discountInfo_template = Handlebars.compile(document.querySelector('#cartOffcanvasDicountInfoHandlebars').innerHTML);
            const discount = discountInfo_template(res.discount);
            document.querySelector("#cartOffcanvasDiscount").innerHTML = discount;

            if (document.querySelector("#checkoutMainPage")) {
                load_cart();
                // setTimeout(load_cart, 3000);
            }
        } else {
            document.querySelector("#cartOffcanvasCloseBtn").disabled = false;
            enable_buttons();
            prevent_default = false;
            document.querySelector("#applyDiscountSpinner").hidden = true;
            document.querySelector("#cartDiscountError").innerHTML = res.message;
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
    request.open('GET', '/store/cart/clear/');

    document.querySelector("#cartOffcanvasCloseBtn").disabled = true;
    disable_buttons();
    prevent_default = true;
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            document.querySelector("#cartOffcanvasCloseBtn").disabled = false;
            enable_buttons();
            prevent_default = false;
            document.querySelector("#cartOffcanvasCloseBtn").click();
            update_cart_count(0);
            if (document.querySelector("#checkoutMainPage")) {
                location.reload();
                // setTimeout(load_cart, 3000);
            }
        }
    };
    request.send();
    return false;
}