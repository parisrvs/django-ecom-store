document.addEventListener("DOMContentLoaded", () => {
    get_user();
});


function get_user() {
    const request = new XMLHttpRequest();
    request.open('GET', '/store/profile/get-user/');

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            last_login = new Date(Date.parse(res.user.last_login))
            date_joined = new Date(Date.parse(res.user.date_joined))
            res.user.last_login = last_login.toLocaleString()
            res.user.date_joined = date_joined.toLocaleString()

            const details_template = Handlebars.compile(document.querySelector('#accountDetailsHandlebars').innerHTML);
            const details = details_template({"user": res.user, "address": res.address});
            document.querySelector("#user_info").innerHTML = details;
        }
    };

    request.send();
    return false;
}


function displayAddAddressFormModal(event) {
    event.preventDefault();
    const details_template = Handlebars.compile(document.querySelector('#addAddressFormHandlebars').innerHTML);
    const details = details_template();
    document.querySelector("#addAddressFormDiv").innerHTML = details;
    document.querySelector("#addAddressModalBtn").click();

    const addAddressModal = document.getElementById('addAddressModal')
    const addAddressFormInputFirstName = document.getElementById('addAddressFormInputFirstName')
    addAddressModal.addEventListener('shown.bs.modal', () => {
        addAddressFormInputFirstName.focus()
    })
    return false;
}


function addAddress(event) {
    event.preventDefault();
    let first_name = document.querySelector("#addAddressFormInputFirstName").value.replace(/^\s+|\s+$/g, '');
    let last_name = document.querySelector("#addAddressFormInputLastName").value.replace(/^\s+|\s+$/g, '');
    let email = document.querySelector("#addAddressFormInputEmail").value.replace(/^\s+|\s+$/g, '');
    let mobile = document.querySelector("#addAddressFormInputMobile").value.replace(/^\s+|\s+$/g, '');
    let landline = document.querySelector("#addAddressFormInputTelephone").value.replace(/^\s+|\s+$/g, '');
    let landmark = document.querySelector("#addAddressFormInputLandmark").value.replace(/^\s+|\s+$/g, '');
    let address1 = document.querySelector("#addAddressFormInputAddresss1").value.replace(/^\s+|\s+$/g, '');
    let address2 = document.querySelector("#addAddressFormInputAddresss2").value.replace(/^\s+|\s+$/g, '');
    let city = document.querySelector("#addAddressFormInputCity").value.replace(/^\s+|\s+$/g, '');
    let pincode = document.querySelector("#addAddressFormInputPincode").value.replace(/^\s+|\s+$/g, '');
    let state = document.querySelector("#addAddressFormInputState").value.replace(/^\s+|\s+$/g, '');
    let country = document.querySelector("#addAddressFormInputCountry").value.replace(/^\s+|\s+$/g, '');

    if (!first_name || !last_name || !email || !mobile || !landmark || !address1 || !city || !pincode || !state || !country) {
        document.getElementById('addAddressFormInputFirstName').focus();
        document.querySelector("#addAddressError").innerHTML = "Incomplete Form";
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
            enable();
            prevent_default = false;
            document.querySelector("#addAddressModalCloseBtn").click();
            get_user();
        } else {
            enable();
            prevent_default = false;
            document.getElementById('addAddressFormInputFirstName').focus();
            document.querySelector("#addAddressError").innerHTML = res.message;
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


function makeAddressPrimary(event, address_id) {
    event.preventDefault();

    let spinnerID = `makeAddressPrimarySpinner${address_id}`;
    let spinner = document.getElementById(spinnerID);

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/profile/make-address-primary/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    prevent_default = true;
    spinner.hidden = false;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            get_user();
        } 
        enable();
        prevent_default = false;
        spinner.hidden = true;
    };

    const data = new FormData();
    data.append('address_id', address_id);
    request.send(data);
    return false;
}


function deleteAddress(event, address_id) {
    event.preventDefault();
    let c = confirm("Are you sure you want to delete this address?");
    if (c) {
        let spinnerID = `deleteAddressSpinner${address_id}`;
        let spinner = document.getElementById(spinnerID);

        const csrftoken = getCookie('csrftoken');
        const request = new XMLHttpRequest();
        request.open('POST', '/store/profile/delete-address/');
        request.setRequestHeader("X-CSRFToken", csrftoken);

        disable();
        prevent_default = true;
        spinner.hidden = false;

        request.onload = () => {
            const res = JSON.parse(request.responseText);
            if (res.success) {
                get_user();
            } 
            enable();
            prevent_default = false;
            spinner.hidden = true;
        };

        const data = new FormData();
        data.append('address_id', address_id);
        request.send(data);
    }
    return false;
}


function displayEditAddressModal(event, address_id) {
    event.preventDefault();
    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/profile/get-address/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            const details_template = Handlebars.compile(document.querySelector('#editAddressFormHandlebars').innerHTML);
            const details = details_template(res.address);
            document.querySelector("#editAddressFormDiv").innerHTML = details;
            document.querySelector("#editAddressModalBtn").click();

            const editAddressModal = document.getElementById('editAddressModal')
            const editAddressFormInputFirstName = document.getElementById('editAddressFormInputFirstName')
            editAddressModal.addEventListener('shown.bs.modal', () => {
                editAddressFormInputFirstName.focus()
            })
        }
    };

    const data = new FormData();
    data.append('address_id', address_id);
    request.send(data);
    return false;
}


function editAddress(event, address_id) {
    event.preventDefault();

    let first_name = document.querySelector("#editAddressFormInputFirstName").value.replace(/^\s+|\s+$/g, '');
    let last_name = document.querySelector("#editAddressFormInputLastName").value.replace(/^\s+|\s+$/g, '');
    let email = document.querySelector("#editAddressFormInputEmail").value.replace(/^\s+|\s+$/g, '');
    let mobile = document.querySelector("#editAddressFormInputMobile").value.replace(/^\s+|\s+$/g, '');
    let landline = document.querySelector("#editAddressFormInputTelephone").value.replace(/^\s+|\s+$/g, '');
    let landmark = document.querySelector("#editAddressFormInputLandmark").value.replace(/^\s+|\s+$/g, '');
    let address1 = document.querySelector("#editAddressFormInputAddresss1").value.replace(/^\s+|\s+$/g, '');
    let address2 = document.querySelector("#editAddressFormInputAddresss2").value.replace(/^\s+|\s+$/g, '');
    let city = document.querySelector("#editAddressFormInputCity").value.replace(/^\s+|\s+$/g, '');
    let pincode = document.querySelector("#editAddressFormInputPincode").value.replace(/^\s+|\s+$/g, '');
    let state = document.querySelector("#editAddressFormInputState").value.replace(/^\s+|\s+$/g, '');
    let country = document.querySelector("#editAddressFormInputCountry").value.replace(/^\s+|\s+$/g, '');

    if (!first_name || !last_name || !email || !mobile || !landmark || !address1 || !city || !pincode || !state || !country) {
        document.getElementById('editAddressFormInputFirstName').focus();
        document.querySelector("#editAddressError").innerHTML = "Incomplete Form";
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/store/profile/edit-address/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            prevent_default = false;
            document.querySelector("#editAddressModalCloseBtn").click();
            get_user();
        } else {
            enable();
            prevent_default = false;
            document.getElementById('editAddressFormInputFirstName').focus();
            document.querySelector("#editAddressError").innerHTML = res.message;
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
    data.append('address_id', address_id);
    request.send(data);
    return false;
}