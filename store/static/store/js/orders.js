document.addEventListener("DOMContentLoaded", ()=>{
    document.querySelectorAll(".utcTime").forEach(s => {
        s.innerHTML = new Date(Date.parse(s.innerHTML)).toLocaleString();
    });
});


function cancelOrder(event, order_id) {
    event.preventDefault();
    let c = confirm("Are you sure you want to cancel this order?");
    if (c) {
        var spinner = document.querySelector("#cancelOrderSpinner");
    
        const csrftoken = getCookie('csrftoken');
        const request = new XMLHttpRequest();
        request.open('POST', '/store/orders/cancel/');
        request.setRequestHeader("X-CSRFToken", csrftoken);

        disable();
        prevent_default = true;
        spinner.hidden = false;

        request.onload = () => {
            const res = JSON.parse(request.responseText);
            if (res.success) {
                enable();
                prevent_default = false;
                spinner.hidden = true;
                window.location.replace(res.redirect_url);
            } else {
                enable();
                prevent_default = false;
                spinner.hidden = true;
                location.reload();
            }
        };

        const data = new FormData();
        data.append('order_id', order_id);
        request.send(data);
    }
    return false;
}