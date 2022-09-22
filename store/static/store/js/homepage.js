function categorySelected() {
    clistID = "filterCategoryListOffcanvas";
    plistID = "filterProductListOffcanvas";
    slistID = "filterSortItemsOffcanvas";
    let category = document.getElementById(clistID).value.replace(/^\s+|\s+$/g, '');
    
    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/get-products/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.products) {
            const details_template = Handlebars.compile(document.querySelector('#productFilterOptionsHandlebars').innerHTML);
            const details = details_template({"products": res.products});
            document.getElementById(plistID).innerHTML = details;

            const details_template_sort = Handlebars.compile(document.querySelector('#sortFilterOptionsHandlebars').innerHTML);
            const details_sort = details_template_sort();
            document.getElementById(slistID).innerHTML = details_sort;
        }
        enable();
        prevent_default = false;
    };

    const data = new FormData();
    data.append('category', category);
    request.send(data);
    return false;
}


function add2cart(event, product_id) {
    event.preventDefault();

    let inputID = `addToCartInput${product_id}`;
    let cartIconID = `cartIcon${product_id}`;
    let cartSubmitBtn = `cartSubmitBtn${product_id}`;
    let qty = document.getElementById(inputID).value.replace(/^\s+|\s+$/g, '');

    if (!qty || isNaN(qty) || qty < 1) {
        document.getElementById(inputID).value = '';
        document.getElementById(cartSubmitBtn).blur();
        document.getElementById(cartIconID).innerHTML = '<i class="bi bi-cart-x text-danger"></i>';
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/add-to-cart/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            document.getElementById(cartIconID).innerHTML = '<i class="bi bi-cart-check text-success"></i>'
            update_cart_count(res.count);
            document.getElementById(inputID).value = '';
        } else {
            document.getElementById(cartIconID).innerHTML = '<i class="bi bi-cart-x text-danger"></i>';
            if (res.out_of_stock) {
                document.getElementById(inputID).value = res.out_of_stock;
            } else {
                document.getElementById(inputID).value = '';
            }
        }
        document.getElementById(cartSubmitBtn).blur();
    };

    const data = new FormData();
    data.append('qty', qty);
    data.append('variation_id', product_id);
    request.send(data);
    return false;
}


function checkDeliverability(event, variation_id) {
    event.preventDefault();

    document.querySelector("#checkPincodeInfoSuccess").innerHTML = '';
    document.querySelector("#checkPincodeInfoDanger").innerHTML = '';

    let pincode = document.querySelector("#checkPincodeFormInput").value.replace(/^\s+|\s+$/g, '');

    if (!pincode) {
        document.querySelector("#checkPincodeFormInputBtn").blur();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/check-deliverability/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            document.querySelector("#checkPincodeInfoSuccess").innerHTML = res.message;
        } else {
            document.querySelector("#checkPincodeInfoDanger").innerHTML = res.message;
        }
        enable();
        prevent_default = false;
        document.querySelector("#checkPincodeFormInputBtn").blur();
        document.querySelector("#checkPincodeFormInput").value = '';
    };

    const data = new FormData();
    data.append('pincode', pincode);
    data.append('variation_id', variation_id);
    request.send(data);
    return false;
}