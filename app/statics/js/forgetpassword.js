document.addEventListener('DOMContentLoaded', () => {

    const stepEmail  = document.getElementById('step-email');
    const stepReset  = document.getElementById('step-reset');
    const emailInput = document.getElementById('reset-email');
    const emailAlert = document.getElementById('email-alert');
    const resetAlert = document.getElementById('reset-alert');
    const checkBtn   = document.getElementById('check-email-btn');
    const resetBtn   = document.getElementById('reset-btn');

    let verifiedEmail = '';

    function showAlert(el, message, type) {
        el.textContent = message;
        el.style.display = 'block';
        if (type === 'error') {
            el.style.background = '#fef2f2';
            el.style.color      = '#dc2626';
            el.style.border     = '1px solid #fca5a5';
        } else {
            el.style.background = '#f0fdf4';
            el.style.color      = '#16a34a';
            el.style.border     = '1px solid #86efac';
        }
    }

    function hideAlert(el) {
        el.style.display = 'none';
        el.textContent = '';
    }

    // STEP 1 — Check email
    checkBtn.addEventListener('click', async () => {
        hideAlert(emailAlert);
        const email = (emailInput.value || '').trim();

        if (!email) {
            showAlert(emailAlert, 'Please enter your email address.', 'error');
            return;
        }

        checkBtn.disabled    = true;
        checkBtn.textContent = 'Checking...';

        try {
            const res  = await fetch('/forget-password/check-email', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ email: email }),
            });
            const data = await res.json();

            if (data.status === 'success') {
                verifiedEmail = email;
                stepEmail.style.display = 'none';
                stepReset.style.display = 'block';
            } else {
                showAlert(emailAlert, data.message || 'No account found with this email.', 'error');
            }
        } catch (err) {
            showAlert(emailAlert, 'Network error. Please try again.', 'error');
        } finally {
            checkBtn.disabled    = false;
            checkBtn.textContent = 'Continue';
        }
    });

    // Allow pressing Enter on email field
    emailInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') checkBtn.click();
    });

    // STEP 2 — Reset password
    resetBtn.addEventListener('click', async () => {
        hideAlert(resetAlert);
        const newPw  = document.getElementById('new-password').value;
        const confPw = document.getElementById('confirm-password').value;

        if (!newPw || !confPw) {
            showAlert(resetAlert, 'Please fill in both password fields.', 'error');
            return;
        }
        if (newPw.length < 8) {
            showAlert(resetAlert, 'Password must be at least 8 characters.', 'error');
            return;
        }
        if (newPw !== confPw) {
            showAlert(resetAlert, 'Passwords do not match.', 'error');
            return;
        }

        resetBtn.disabled    = true;
        resetBtn.textContent = 'Resetting...';

        try {
            const res  = await fetch('/forget-password/reset', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({
                    email:            verifiedEmail,
                    new_password:     newPw,
                    confirm_password: confPw,
                }),
            });
            const data = await res.json();

            if (data.status === 'success') {
                showAlert(resetAlert, 'Password reset successfully! Redirecting to login...', 'success');
                setTimeout(() => { window.location.href = '/login'; }, 2000);
            } else {
                showAlert(resetAlert, data.message || 'Something went wrong.', 'error');
                resetBtn.disabled    = false;
                resetBtn.textContent = 'Reset Password';
            }
        } catch (err) {
            showAlert(resetAlert, 'Network error. Please try again.', 'error');
            resetBtn.disabled    = false;
            resetBtn.textContent = 'Reset Password';
        }
    });

});