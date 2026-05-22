document.addEventListener('DOMContentLoaded', () => {
    const forgetForm = document.getElementById('forget-password-form');
    if (forgetForm) {
        forgetForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log('HireNest Password reset link request captured client-side.');
        });
    }
});

