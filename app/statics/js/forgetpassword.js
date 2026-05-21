document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('forget-form');
    if (!form) return;
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const email = document.getElementById('fp-email').value;
        alert('If an account exists for ' + email + ', a reset link will be sent.');
        form.reset();
        window.location.href = '/login';
    });
});

