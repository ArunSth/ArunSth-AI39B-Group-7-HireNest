document.addEventListener('DOMContentLoaded', function () {
    // Optionally auto-redirect after logout
    setTimeout(() => {
        const loginLink = document.querySelector('.btn-submit');
        if (!loginLink) return;
        // keep as link to allow user to click; no auto-redirect by default
    }, 1000);
});

