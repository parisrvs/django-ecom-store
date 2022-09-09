function get_variations(product_id) {
    let btn_id = `add_variation_btn_${product_id}`;
    document.getElementById(btn_id).blur();

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/products/get-variations/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            const details_template = Handlebars.compile(document.querySelector('#productVariationsHandlebars').innerHTML);
            const details = details_template({"title": res.product_name, "variations": res.variations});
            document.querySelector("#productVariationsModalDialog").innerHTML = details;
            document.querySelector("#productVariationsModalBtn").click();
        } else {
            alert(res.message);
        }
    };

    const data = new FormData();
    data.append('product_id', product_id);
    request.send(data);
    return false;
}


function add2cart(event, var_id) {
    event.preventDefault();
    let input_id = `variationQtyFormInput${var_id}`;
    let btn_id = `add2cartBtn${var_id}`;
    let error_id = `add2cartError${var_id}`;
    let cartIconId = `cartCheckIcon${var_id}`;
    let spinnerID = `add2cartSpinner${var_id}`
    let spinner = document.getElementById(spinnerID);

    let qty = document.getElementById(input_id).value.replace(/^\s+|\s+$/g, '');
    if (!qty || isNaN(qty) || qty <= 0) {
        document.getElementById(btn_id).blur();
        document.getElementById(input_id).value = '';
        document.getElementById(input_id).focus();
        document.getElementById(cartIconId).style.color = "red";
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/products/add-to-cart/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    prevent_default = true;
    disable_buttons();
    spinner.hidden = false;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            prevent_default = false;
            enable_buttons();
            spinner.hidden = true;
            document.getElementById(btn_id).blur();
            document.getElementById(input_id).value = '';
            document.getElementById(cartIconId).style.color = "green";
            update_cart_count(res.count);
        } else {
            prevent_default = false;
            enable_buttons();
            spinner.hidden = true;
            document.getElementById(error_id).innerHTML = res.message;
            document.getElementById(cartIconId).style.color = "red";
        }
    };

    const data = new FormData();
    data.append('var_id', var_id);
    data.append('qty', qty);
    request.send(data);
    return false;
}


// const registerVerificationModal = document.getElementById('registerVerificationModal');
// const registerVerifyCode = document.getElementById('registerVerifyCode');
// registerVerificationModal.addEventListener('shown.bs.modal', () => {
//     registerVerifyCode.focus();
// })
