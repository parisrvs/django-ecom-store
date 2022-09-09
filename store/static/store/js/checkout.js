document.addEventListener("DOMContentLoaded", () => {
    load_cart();
});


function load_cart() {
    const request = new XMLHttpRequest();
    request.open('GET', '/store/cart/');
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            const details_template = Handlebars.compile(document.querySelector('#checkoutItemsHandlebars').innerHTML);
            const details = details_template({"cart": res.cart, "total": res.total, "currency": res.currency, "items_count": res.items_count});
            document.querySelector("#confirmCheckoutDiv").innerHTML = details;

            if (res.discount) {
                const discountInfo_template = Handlebars.compile(document.querySelector('#checkoutDicountInfoHandlebars').innerHTML);
                const discount = discountInfo_template(res.discount);
                document.querySelector("#checkoutDiscountInfoDiv").innerHTML = discount;
            }

            if (res.delivery_address) {
                const address_template = Handlebars.compile(document.querySelector('#checkoutSelectedDeliveryAddressHandlebars').innerHTML);
                const address = address_template(res.delivery_address);
                document.querySelector("#checkoutDevileryAddressDiv").innerHTML = address;
            } else {
                const address_template = Handlebars.compile(document.querySelector('#checkoutDeliveryAddressFormHandlebars').innerHTML);
                const address = address_template();
                document.querySelector("#checkoutDevileryAddressDiv").innerHTML = address;
            }
        } else {
            location.reload();
        }
    };
    request.send();
    return false;
}


function selectSavedAddress(event) {
    event.preventDefault();

    const request = new XMLHttpRequest();
    request.open('GET', '/store/get-user-address/');
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            const details_template = Handlebars.compile(document.querySelector('#checkoutSelectDeliveryAddressHandlebars').innerHTML);
            const details = details_template({"address": res.address});
            document.querySelector("#savedDeliveryAddresses").innerHTML = details;
            document.querySelector("#savedDeliveryAddressModalBtn").click();
        } else {
            document.querySelector("#noSavedDeliveryAddressMessageModalBtn").click();
        }
    };
    request.send();
    return false;
}


function selectThisDeliveryAddress (event, address_id) {
    event.preventDefault();

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/cart/add-delivery-address/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable_buttons();
    prevent_default = true;
    let spinner_id = `selectThisDeliveryAddressAnchorTagSpinner${address_id}`;
    let spinner = document.getElementById(spinner_id);
    spinner.hidden = false;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            const address_template = Handlebars.compile(document.querySelector('#checkoutSelectedDeliveryAddressHandlebars').innerHTML);
            const address = address_template(res.delivery_address);
            document.querySelector("#checkoutDevileryAddressDiv").innerHTML = address;
            
            enable_buttons();
            prevent_default = false;
            spinner.hidden = true;
            document.querySelector("#savedDeliveryAddressModalCloseBtn").click();
        } else {
            enable_buttons();
            prevent_default = false;
            spinner.hidden = true;
            document.querySelector("#savedDeliveryAddressModalCloseBtn").click();
            alert(res.message);
        }
    };

    const data = new FormData();
    data.append('address_id', address_id);
    request.send(data);
    return false;
}


function removeSelectedDeliveryAddress(event, address_id) {
    event.preventDefault();

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/cart/remove-delivery-address/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable_buttons();
    prevent_default = true;
    let spinner_id = `removeSelectedDeliveryAddressAnchorTagSpinner${address_id}`;
    let spinner = document.getElementById(spinner_id);
    spinner.hidden = false;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            prevent_default = false;
            spinner.hidden = true;
            enable_buttons();
            const address_template = Handlebars.compile(document.querySelector('#checkoutDeliveryAddressFormHandlebars').innerHTML);
            const address = address_template();
            document.querySelector("#checkoutDevileryAddressDiv").innerHTML = address;
        } else {
            prevent_default = false;
            spinner.hidden = true;
            enable_buttons();
            alert(res.message);
        }
    };

    const data = new FormData();
    data.append('address_id', address_id);
    request.send(data);
    return false;
}


function addNewDeliveryAddress(event) {
    event.preventDefault();

    let first_name = document.querySelector("#checkoutFormInputFirstName").value.replace(/^\s+|\s+$/g, '');
    let last_name = document.querySelector("#checkoutFormInputLastName").value.replace(/^\s+|\s+$/g, '');
    let mobile = document.querySelector("#checkoutFormInputMobile").value.replace(/^\s+|\s+$/g, '');
    let homephone = document.querySelector("#checkoutFormInputLandline").value.replace(/^\s+|\s+$/g, '');
    let address1 = document.querySelector("#checkoutFormInputAddress1").value.replace(/^\s+|\s+$/g, '');
    let address2 = document.querySelector("#checkoutFormInputAddress2").value.replace(/^\s+|\s+$/g, '');
    let city = document.querySelector("#checkoutFormInputCity").value.replace(/^\s+|\s+$/g, '');
    let pincode = document.querySelector("#checkoutFormInputPincode").value.replace(/^\s+|\s+$/g, '');
    let state = document.querySelector("#checkoutFormInputState").value.replace(/^\s+|\s+$/g, '');
    let country = document.querySelector("#checkoutFormInputCountry").value.replace(/^\s+|\s+$/g, '');
    let landmark = document.querySelector("#checkoutFormInputLandmark").value.replace(/^\s+|\s+$/g, '');
    let email = document.querySelector("#checkoutFormInputEmail").value.replace(/^\s+|\s+$/g, '');

    if (!first_name || !last_name || !mobile || !address1 || !city || !state || !pincode || !state || !country || !landmark || !email) {
        document.querySelector("#addNewDeliveryAddressError").innerHTML = "Incomplete Form";
        document.querySelector("#checkoutFormInputFirstName").focus();
        return false;
    }

    let spinner = document.querySelector("#addNewAddressFormSpinner");

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/cart/add-new-delivery-address/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable_buttons();
    prevent_default = true;
    spinner.hidden = false;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            prevent_default = false;
            spinner.hidden = true;
            enable_buttons();
            const address_template = Handlebars.compile(document.querySelector('#checkoutSelectedDeliveryAddressHandlebars').innerHTML);
            const address = address_template(res.delivery_address);
            document.querySelector("#checkoutDevileryAddressDiv").innerHTML = address;
        } else {
            prevent_default = false;
            spinner.hidden = true;
            enable_buttons();
            document.querySelector("#addNewDeliveryAddressError").innerHTML = res.message;
            document.querySelector("#checkoutFormInputFirstName").focus();
        }
    };

    const data = new FormData();
    data.append('first_name', first_name);
    data.append('last_name', last_name);
    data.append('mobile', mobile);
    data.append('homephone', homephone);
    data.append('address1', address1);
    data.append('address2', address2);
    data.append('city', city);
    data.append('pincode', pincode);
    data.append('state', state);
    data.append('country', country);
    data.append('landmark', landmark);
    data.append('email', email);

    request.send(data);
    return false;
}


function place_order(event) {
    event.preventDefault();
    let time = document.querySelector("#OrderConfirmationInputTime").value.replace(/^\s+|\s+$/g, '');
    let date = document.querySelector("#OrderConfirmationInputDate").value.replace(/^\s+|\s+$/g, '');
    let info = document.querySelector("#OrderConfirmationInputInfo").value.replace(/^\s+|\s+$/g, '');

    if (info && info.length > 200) {
        document.querySelector("#placeOrderError").innerHTML = "Maxinum 200 characters allowed.";
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/checkout/place-order/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    let spinner = document.querySelector("#placeOrderConfirmationSpinner");
    disable_buttons();
    prevent_default = true;
    spinner.hidden = false;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            prevent_default = false;
            spinner.hidden = true;
            window.location.replace(res.return_url);
        } else {
            enable_buttons();
            prevent_default = false;
            spinner.hidden = true;
            document.querySelector("#placeOrderError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('time', time);
    data.append('date', date);
    data.append('info', info);
    request.send(data);
    return false;
}