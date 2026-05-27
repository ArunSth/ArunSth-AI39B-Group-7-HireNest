document.addEventListener('DOMContentLoaded', () => {

    // =========================================================================
    // 1. THEME SWITCHER
    // =========================================================================
    const themeToggleBtn = document.getElementById('theme-toggle');
    const rootElement = document.documentElement;

    const savedTheme = localStorage.getItem('theme') || 'light';
    rootElement.setAttribute('data-theme', savedTheme);
    updateThemeIconStyle(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = rootElement.getAttribute('data-theme');
            const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
            rootElement.setAttribute('data-theme', nextTheme);
            localStorage.setItem('theme', nextTheme);
            updateThemeIconStyle(nextTheme);
        });
    }

    function updateThemeIconStyle(theme) {
        if (!themeToggleBtn) return;
        if (theme === 'dark') {
            themeToggleBtn.className = 'fa-solid fa-moon';
            themeToggleBtn.style.color = '#f59e0b';
        } else {
            themeToggleBtn.className = 'fa-solid fa-sun';
            themeToggleBtn.style.color = 'inherit';
        }
    }

    // =========================================================================
    // 2. DOM SELECTORS
    // =========================================================================
    const authModal      = document.getElementById('auth-modal');
    const signupNavBtn   = document.getElementById('signup-nav-btn');
    const loginNavBtn    = document.getElementById('login-nav-btn');
    const closeModalBtn  = document.getElementById('close-modal');
    const modalTitle     = document.getElementById('modal-title');
    const authForm       = document.getElementById('auth-form');
    const submitAuthBtn  = document.getElementById('submit-auth-btn');
    const switchFormLink = document.getElementById('switch-form-link');
    const switchText     = document.getElementById('switch-text');
    const signupOnlyFields = document.querySelectorAll('.signup-only');
    const emailLabel     = document.getElementById('modal-email-label');
    const emailInput     = document.getElementById('user-email');
    const modalRoleInput = document.getElementById('modal-role');
    const modalAlert     = document.getElementById('modal-alert');

    const targetCandidate = document.getElementById('target-candidate');
    const targetRecruiter = document.getElementById('target-recruiter');

    let isSignUpMode = true;
    let currentRole  = 'job_seeker';

    // =========================================================================
    // 3. OPEN / CLOSE MODAL
    // =========================================================================
    if (signupNavBtn) {
        signupNavBtn.addEventListener('click', () => {
            configureModalMode(true, 'job_seeker');
            authModal.style.display = 'flex';
        });
    }

    if (loginNavBtn) {
        loginNavBtn.addEventListener('click', () => {
            configureModalMode(false);
            authModal.style.display = 'flex';
        });
    }

    if (targetCandidate) {
        targetCandidate.addEventListener('click', () => {
            configureModalMode(true, 'job_seeker');
            authModal.style.display = 'flex';
        });
    }

    if (targetRecruiter) {
        targetRecruiter.addEventListener('click', () => {
            configureModalMode(true, 'employer');
            authModal.style.display = 'flex';
        });
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => authModal.style.display = 'none');
    }

    window.addEventListener('click', (event) => {
        if (event.target === authModal) authModal.style.display = 'none';
    });

    if (switchFormLink) {
        switchFormLink.addEventListener('click', (event) => {
            event.preventDefault();
            configureModalMode(!isSignUpMode, currentRole);
        });
    }

    // =========================================================================
    // 4. CONFIGURE MODAL MODE (signup / login, role)
    // =========================================================================
    function configureModalMode(targetIsSignUp, role = 'job_seeker') {
        isSignUpMode = targetIsSignUp;
        currentRole  = role;
        if (authForm) authForm.reset();
        hideAlert();

        if (isSignUpMode) {
            if (modalTitle)    modalTitle.textContent     = 'Create an account';
            if (submitAuthBtn) submitAuthBtn.textContent  = 'Sign Up';
            if (switchText)    switchText.textContent     = 'Already have an account?';
            if (switchFormLink) switchFormLink.textContent = 'Log In';
            if (authForm)      authForm.action            = '/register';
            if (modalRoleInput) modalRoleInput.value      = currentRole;

            signupOnlyFields.forEach(field => {
                field.style.display = 'flex';
                const input = field.querySelector('input');
                if (input) input.required = true;
            });

            if (currentRole === 'employer') {
                if (emailLabel) emailLabel.textContent  = 'Company Email*';
                if (emailInput) emailInput.placeholder  = 'eg. bruce@wayne.enterprises';
            } else {
                if (emailLabel) emailLabel.textContent  = 'Email*';
                if (emailInput) emailInput.placeholder  = 'eg. janecopper@xyz.com';
            }
        } else {
            if (modalTitle)    modalTitle.textContent     = 'Log In';
            if (submitAuthBtn) submitAuthBtn.textContent  = 'Welcome Back';
            if (switchText)    switchText.textContent     = "Don't have an account?";
            if (switchFormLink) switchFormLink.textContent = 'Sign Up';
            if (authForm)      authForm.action            = '/login';

            signupOnlyFields.forEach(field => {
                field.style.display = 'none';
                const input = field.querySelector('input');
                if (input) input.required = false;
            });

            if (emailLabel) emailLabel.textContent = 'Email Address';
            if (emailInput) emailInput.placeholder = 'name@gmail.com';
        }
    }

    // =========================================================================
    // 5. ALERT HELPERS
    // =========================================================================
    function showAlert(message, type) {
        if (!modalAlert) return;
        modalAlert.textContent = message;
        modalAlert.style.display = 'block';
        if (type === 'error') {
            modalAlert.style.background = '#fef2f2';
            modalAlert.style.color      = '#dc2626';
            modalAlert.style.border     = '1px solid #fca5a5';
        } else {
            modalAlert.style.background = '#f0fdf4';
            modalAlert.style.color      = '#16a34a';
            modalAlert.style.border     = '1px solid #86efac';
        }
    }

    function hideAlert() {
        if (modalAlert) modalAlert.style.display = 'none';
    }

    // =========================================================================
    // 6. FORM SUBMISSION — REAL AJAX TO BACKEND
    // =========================================================================
    if (authForm) {
        authForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            hideAlert();

            if (submitAuthBtn) {
                submitAuthBtn.disabled    = true;
                submitAuthBtn.textContent = 'Please wait...';
            }

            // Build clean FormData with field names the backend expects,
            // regardless of the HTML input name attributes (user-email vs email etc.)
            const rawData = new FormData(authForm);
            const formData = new FormData();
            const endpoint = isSignUpMode ? '/register' : '/login';

            formData.append('email',    rawData.get('user-email')    || rawData.get('email')    || '');
            formData.append('password', rawData.get('user-password') || rawData.get('password') || '');

            if (isSignUpMode) {
                formData.append('name',  rawData.get('user-name')  || rawData.get('name')  || '');
                formData.append('phone', rawData.get('user-phone') || rawData.get('phone') || '');
                formData.append('role',  rawData.get('role') || currentRole);
            }

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                    body: formData,
                });

                const data = await response.json();

                if (data.status === 'ok') {
                    showAlert(data.message, 'success');
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 600);
                } else {
                    showAlert(data.message || 'Something went wrong.', 'error');
                    if (submitAuthBtn) {
                        submitAuthBtn.disabled    = false;
                        submitAuthBtn.textContent = isSignUpMode ? 'Sign Up' : 'Welcome Back';
                    }
                }
            } catch (err) {
                showAlert('Network error. Please try again.', 'error');
                if (submitAuthBtn) {
                    submitAuthBtn.disabled    = false;
                    submitAuthBtn.textContent = isSignUpMode ? 'Sign Up' : 'Welcome Back';
                }
            }
        });
    }
});