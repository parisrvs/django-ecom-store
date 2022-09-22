document.addEventListener("DOMContentLoaded", ()=>{
    load_checkout_page();
});


function load_checkout_page() {
    const request = new XMLHttpRequest();
    request.open('GET', '/store/get-cart/');

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            if (res.cart.delivery_address) {
                const address_template = Handlebars.compile(document.querySelector('#checkoutPageAddressHandlebars').innerHTML);
                const address = address_template(res.cart.delivery_address);
                document.querySelector("#delivery_address").innerHTML = address;
            } else {
                const address_template = Handlebars.compile(document.querySelector('#checkoutPageAddressFormHandlebars').innerHTML);
                const address = address_template();
                document.querySelector("#delivery_address").innerHTML = address;
                document.querySelector("#addDeliveryAddressFormInputFirstName").focus();
            }
            const details_template = Handlebars.compile(document.querySelector('#checkoutPageCartItemsHandlebars').innerHTML);
            const details = details_template({"cart": res.cart});
            document.querySelector("#cart_items").innerHTML = details;
        } else {
            location.reload();
        }
    };

    request.send();
    return false;
}



function addDeliveryAddress(event) {
    event.preventDefault();
    let first_name = document.querySelector("#addDeliveryAddressFormInputFirstName").value.replace(/^\s+|\s+$/g, '');
    let last_name = document.querySelector("#addDeliveryAddressFormInputLastName").value.replace(/^\s+|\s+$/g, '');
    let email = document.querySelector("#addDeliveryAddressFormInputEmail").value.replace(/^\s+|\s+$/g, '');
    let mobile = document.querySelector("#addDeliveryAddressFormInputMobile").value.replace(/^\s+|\s+$/g, '');
    let landline = document.querySelector("#addDeliveryAddressFormInputTelephone").value.replace(/^\s+|\s+$/g, '');
    let landmark = document.querySelector("#addDeliveryAddressFormInputLandmark").value.replace(/^\s+|\s+$/g, '');
    let address1 = document.querySelector("#addDeliveryAddressFormInputAddresss1").value.replace(/^\s+|\s+$/g, '');
    let address2 = document.querySelector("#addDeliveryAddressFormInputAddresss2").value.replace(/^\s+|\s+$/g, '');
    let city = document.querySelector("#addDeliveryAddressFormInputCity").value.replace(/^\s+|\s+$/g, '');
    let pincode = document.querySelector("#addDeliveryAddressFormInputPincode").value.replace(/^\s+|\s+$/g, '');
    let state = document.querySelector("#addDeliveryAddressFormInputState").value.replace(/^\s+|\s+$/g, '');
    let country = document.querySelector("#addDeliveryAddressFormInputCountry").value.replace(/^\s+|\s+$/g, '');

    if (!first_name || !last_name || !email || !mobile || !landmark || !address1 || !city || !pincode || !state || !country) {
        document.getElementById('addDeliveryAddressFormInputFirstName').focus();
        document.querySelector("#addDeliveryAddressError").innerHTML = "Incomplete Form";
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/profile/add-address/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            selectDeliveryAddress(false, res.address.id);
        } else {
            enable();
            prevent_default = false;
            document.getElementById('addDeliveryAddressFormInputFirstName').focus();
            document.querySelector("#addDeliveryAddressError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('first_name', first_name);
    data.append('last_name', last_name);
    data.append('email', email);
    data.append('mobile', mobile);
    data.append('landline', landline);
    data.append('landmark', landmark);
    data.append('address1', address1);
    data.append('address2', address2);
    data.append('city', city);
    data.append('pincode', pincode);
    data.append('state', state);
    data.append('country', country);
    request.send(data);
    return false;
}


function selectDeliveryAddress(event, address_id) {
    if (event)
        event.preventDefault();
    
    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/checkout/select-delivery-address/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            prevent_default = false;
            const address_template = Handlebars.compile(document.querySelector('#checkoutPageAddressHandlebars').innerHTML);
            const address = address_template(res.address);
            document.querySelector("#delivery_address").innerHTML = address;
            if (document.querySelector("#selectDeliveryAddressModalCloseBtn"))
                document.querySelector("#selectDeliveryAddressModalCloseBtn").click();
            
            const details_template = Handlebars.compile(document.querySelector('#checkoutPageCartItemsHandlebars').innerHTML);
            const details = details_template({"cart": res.cart});
            document.querySelector("#cart_items").innerHTML = details;
        } else {
            enable();
            prevent_default = false;
            location.reload();
        }
    };

    const data = new FormData();
    data.append('address_id', address_id);
    request.send(data);
    return;
}


function displayDeliveryAddress(event) {
    event.preventDefault();
    const request = new XMLHttpRequest();
    request.open('GET', '/store/checkout/get-delivery-address/');

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            const address_template = Handlebars.compile(document.querySelector('#checkoutPageSelectAddressHandlebars').innerHTML);
            const address = address_template({"address": res.address});
            document.querySelector("#selectDeliveryAddressModalDiv").innerHTML = address;
            document.querySelector("#selectDeliveryAddressModalBtn").click();
        } else {
            location.reload();
        }
    };

    request.send();
    return false;
}


function removeSelectedDeliveryAddress(event, address_id) {
    event.preventDefault();
    
    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/checkout/remove-selected-delivery-address/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    let spinner = document.querySelector("#removeDeliveryAddressSpinner");
    disable();
    prevent_default = true;
    spinner.hidden = false;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            prevent_default = false;
            spinner.hidden = true;
            const address_template = Handlebars.compile(document.querySelector('#checkoutPageAddressFormHandlebars').innerHTML);
            const address = address_template();
            document.querySelector("#delivery_address").innerHTML = address;
            document.querySelector("#addDeliveryAddressFormInputFirstName").focus();

            const details_template = Handlebars.compile(document.querySelector('#checkoutPageCartItemsHandlebars').innerHTML);
            const details = details_template({"cart": res.cart});
            document.querySelector("#cart_items").innerHTML = details;
        } else {
            enable();
            prevent_default = false;
            spinner.hidden = true;
            location.reload();
        }
    };

    const data = new FormData();
    data.append('address_id', address_id);
    request.send(data);
    return;
}


function placeOrder(event) {
    event.preventDefault();
    document.querySelector("#placeOrderError").innerHTML = '';

    let payment_method = document.querySelector('input[name="checkoutPaymentMethod"]:checked').value.replace(/^\s+|\s+$/g, '');
    let preferred_date = document.querySelector("#checkoutPreferredDate").value.replace(/^\s+|\s+$/g, '');
    let preferred_time = document.querySelector("#checkoutPreferredTime").value.replace(/^\s+|\s+$/g, '');

    var date = '';
    if (preferred_date && preferred_time)
        date = new Date(preferred_date + ' ' + preferred_time).toUTCString();
    else if (preferred_date)
        date = new Date(preferred_date).toUTCString();
    
    if (!payment_method) {
        document.querySelector("#placeOrderError").innerHTML = "Please select a payment method.";
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/checkout/place-order/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    let spinner = document.querySelector("#chechoutPlaceOrderSpinner");
    disable();
    prevent_default = true;
    spinner.hidden = false;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            prevent_default = false;
            spinner.hidden = true;
            window.location.replace(res.return_url);
        } else {
            if (res.reload) {
                prevent_default = false;
                window.location.replace(res.reload_url);
            } else {
                enable();
                spinner.hidden = true;
                prevent_default = false;
                document.querySelector("#placeOrderError").innerHTML = res.message;
            }
        }
    };

    const data = new FormData();
    data.append('payment_method', payment_method);
    data.append('datetime', date);
    request.send(data);
    return;
}