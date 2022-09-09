function cancel_order(event, order_id) {
    event.preventDefault();

    let reason = document.querySelector("#OrderCancellationInputReason").value.replace(/^\s+|\s+$/g, '');
    if (reason && reason.length > 200) {
        document.querySelector("#cancelOrderError").innerHTML = "Maxinum 200 characters allowed.";
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/orders/cancel/');
    request.setRequestHeader("X-CSRFToken", csrftoken);
    
    let spinner = document.querySelector("#cancelOrderSpinner")
    disable_buttons();
    prevent_default = true;
    spinner.hidden = false;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            prevent_default = false;
            spinner.hidden = true;
            location.reload();
        } else {
            enable_buttons();
            prevent_default = false;
            spinner.hidden = true;
            document.querySelector("#cancelOrderError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('order_id', order_id);
    data.append('reason', reason);
    request.send(data);
    return false;
}


function displayOrderCancellationModal(order_id) {
    const details_template = Handlebars.compile(document.querySelector('#cancelOrderHandlebars').innerHTML);
    const details = details_template({"order_id": order_id});
    document.querySelector("#orderCancelModalBody").innerHTML = details;
    document.querySelector("#cancelOrderModalBtn").click();
    return;
}