document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registration-form');
    if (!form) return;
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        alert('Registration submitted for ' + email + '.\nImplement server-side handling in controllers.');
        form.reset();
        window.location.href = '/login';
    });
});

