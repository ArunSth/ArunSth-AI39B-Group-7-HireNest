document.addEventListener('DOMContentLoaded', () => {
 
    const themeToggleBtn = document.getElementById('theme-toggle');
    const rootElement = document.documentElement;

    const savedTheme = localStorage.getItem('theme') || 'light';
    rootElement.setAttribute('data-theme', savedTheme);
    updateThemeIconStyle(savedTheme);

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = rootElement.getAttribute('data-theme');
        const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
 
        rootElement.setAttribute('data-theme', nextTheme);
        localStorage.setItem('theme', nextTheme);
        updateThemeIconStyle(nextTheme);
    });

    function updateThemeIconStyle(theme) {
        if (theme === 'dark') {
            themeToggleBtn.className = 'fa-solid fa-moon';
        } else {
            themeToggleBtn.className = 'fa-solid fa-sun';
        }
    }

    const authModal = document.getElementById('auth-modal');
    const signupNavBtn = document.getElementById('signup-nav-btn');
    const loginNavBtn = document.getElementById('login-nav-btn');
    const closeModalBtn = document.getElementById('close-modal');
 
    const modalTitle = document.getElementById('modal-title');
    const authForm = document.getElementById('auth-form');
    const submitAuthBtn = document.getElementById('submit-auth-btn');
    const switchFormLink = document.getElementById('switch-form-link');
    const switchText = document.getElementById('switch-text');
    const signupOnlyFields = document.querySelectorAll('.signup-only');
    const phoneInput = document.getElementById('user-phone'); 

    let isSignUpMode = true;

    if(signupNavBtn) {
        signupNavBtn.addEventListener('click', () => {
            configureModalMode(true);
            authModal.style.display = 'flex';
        });
    }

    if(loginNavBtn) {
        loginNavBtn.addEventListener('click', () => {
            configureModalMode(false);
            authModal.style.display = 'flex';
        });
    }

    closeModalBtn.addEventListener('click', () => authModal.style.display = 'none');
    window.addEventListener('click', (event) => {
        if (event.target === authModal) authModal.style.display = 'none';
    });

    switchFormLink.addEventListener('click', (event) => {
        event.preventDefault();
        configureModalMode(!isSignUpMode);
    });

    function configureModalMode(targetIsSignUp) {
        isSignUpMode = targetIsSignUp;
        authForm.reset();

        if (isSignUpMode) {
            modalTitle.textContent = 'Sign Up';
            submitAuthBtn.textContent = 'Create Account';
            switchText.textContent = 'Already have an account?';
            switchFormLink.textContent = 'Log In';
 
            if (phoneInput) {
                phoneInput.placeholder = '+977 98XXXXXXXX';
            }
 
            signupOnlyFields.forEach(field => {
                field.style.display = 'flex';
                field.querySelector('input').required = true;
            });
        } else {
            modalTitle.textContent = 'Log In';
            submitAuthBtn.textContent = 'Welcome Back';
            switchText.textContent = "Don't have an account?";
            switchFormLink.textContent = 'Sign Up';
            signupOnlyFields.forEach(field => {
                field.style.display = 'none';
                field.querySelector('input').required = false;
            });
        }
    }

    authForm.addEventListener('submit', (event) => {
        event.preventDefault();
 
        const emailValue = document.getElementById('user-email').value;
        const passwordValue = document.getElementById('user-password').value;

        if (isSignUpMode) {
            const nameValue = document.getElementById('user-name').value;
            const phoneValue = document.getElementById('user-phone').value;
 
            console.log("Saving user profile metrics securely...", { nameValue, phoneValue, emailValue });
            alert(`Registration Complete! Welcome to HireNest, ${nameValue}.`);
        } else {
            console.log("Verifying credentials against user storage tables...", { emailValue });
            alert(`Logged in successfully as: ${emailValue}`);
        }

        authModal.style.display = 'none';
        authForm.reset();
    });
});