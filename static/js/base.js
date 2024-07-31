function submitForm(form) {
    $("#overlay").show();
    form.submit();
}

const alertContainer = document.getElementById('alertContainer')
const sendAlert = (message, type) => {
    type = type == 'message' ? 'info' : type;
    const wrapper = document.createElement('div');
    wrapper.innerHTML = [
        `<div class="alert alert-${type} alert-dismissible" role="alert">`,
        `   <div>${message}</div>`,
        `   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`,
        `</div>`
    ].join('');
    alertContainer.append(wrapper);
}


function toTitleCase(str) {
    return str.replace(/\w\S*/g, function(txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
}

window.onload = () => {
    $("#overlay").hide();
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}


window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        $("#overlay").hide();
    }
});